from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from math import log, exp
from music.models import Songs

def trending(limit=20, cache_ttl=90):
    """
    Generate trending tracks list with multiple engagement signals.
    Includes like-based signals similar to Spotify 'save' importance.
    """
    cache_key = f"trending_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now = timezone.now()
    min_date = now - timedelta(days=30)

    # فقط آهنگ‌های منتشر شده و اخیر
    songs_qs = (
        Songs.objects.filter(
            is_published=True,
            release_date__gte=min_date,
        )
        .select_related("genre")
        .prefetch_related(
            "trackartist_set",
            "trackartist_set__artist",
            "liked_by",  # برای کاهش تعداد کوئری‌های شمارش لایک‌ها
        )
    )

    scored = []
    now_hour = now.hour

    for song in songs_qs:
        # مقادیر پایه با fallback امن
        plays_24 = song.plays_last_24h or 0
        total_plays = song.play_count or 0
        total_seconds = song.total_listen_time or 0
        unique_users = song.unique_listeners or 0

        skip_rate = getattr(song, "skip_rate", 0.0) or 0.0               # 0..1
        completion_rate = getattr(song, "completion_rate", 0.0) or 0.0   # 0..1
        session_quality = getattr(song, "session_quality", 0.0) or 0.0   # 0..1
        ai_popularity = getattr(song, "ai_popularity", 0.0) or 0.0       # 0..1
        hourly_plays = getattr(song, "plays_by_hour", {}) or {}

        release_date = song.release_date
        days_old = (now - release_date).days if release_date else 0
        days_old = max(days_old, 0)

        # time-weighted hourly plays: جدیدتر → وزن بیشتر
        tw_score = 0.0
        for hour_str, value in hourly_plays.items():
            try:
                hour = int(hour_str)
            except Exception:
                continue
            if value is None:
                continue

            age_hours = (now_hour - hour) % 24
            age_hours = max(age_hours, 1)
            tw_score += value * (1 / (age_hours ** 1.3))
        tw_score = min(tw_score * 1.2, 60)

        # velocity و رشد
        denom = total_plays + 10  # نرم‌کننده
        velocity = plays_24 / denom if denom else 0
        velocity = min(velocity, 0.8)

        velocity_score = log(plays_24 + 1) * 9
        growth_score = velocity * 55

        # engagement کلی
        avg_listen = total_seconds / total_plays if total_plays > 0 else 0
        engagement_score = (
            log(total_seconds + 1) * 1.8 +
            log(unique_users + 1) * 3 +
            log(avg_listen + 1) * 4
        )

        # skip / completion
        skip_penalty = skip_rate * 20
        completion_bonus = completion_rate * 30

        # کیفیت سشن
        session_score = session_quality * 10

        # viral spike نسبت plays_24 به total_plays
        viral_score = 0
        if total_plays > 15:
            spike = plays_24 / total_plays
            viral_score = 20 if spike > 0.30 else 12 if spike > 0.18 else 0

        # تازگی و decay
        freshness_score = exp(-days_old / 6) * 20
        decay_score = exp(-days_old / 28) * 8

        # سیگنال خارجی/مدل
        ai_score = ai_popularity * 15

        # ضدتقلب: plays per user خیلی بالا → احتمال دستکاری
        manipulation_penalty = 0
        if unique_users > 0:
            ppu = total_plays / unique_users
            manipulation_penalty = 25 if ppu > 30 else 15 if ppu > 18 else 0

        # discovery: اگر کاربرهای یکتا کم ولی رشد 24ساعته خوب
        discovery_score = 10 if (unique_users < 70 and plays_24 > 6) else 0

        # لایک‌ها (شبیه save در اسپاتیفای)
        # توجه: برای جلوگیری از N+1، از prefetch_related("liked_by") استفاده شده
        likes_count = song.liked_by.count()
        # نرخ ذخیره (save rate)
        save_rate = (likes_count / unique_users) if unique_users > 0 else 0.0

        # عامل تازگی: ارزش لایک در روزهای اول بیشتر است
        fresh_factor = exp(-days_old / 20.0)  # کندتر از freshness_score

        # امتیاز پایه لایک‌ها: log-scale برای نرم شدن
        like_base = log(likes_count + 1) * 4.0 * fresh_factor

        # بوست هوشمند: اگر نرخ تکمیل خوب باشد، ارزش save بیشتر
        completion_like_boost = completion_rate * save_rate * 14.0  # اگر زیاد شد، عدد را کم کن

        # محافظه‌کارانه: محدودیت بالا برای اثر لایک
        like_score = min(like_base + completion_like_boost, 22.0)

        # انتخاب آرتیست اصلی برای محدودسازی per-artist
        main_artist = None
        for rel in song.trackartist_set.all():
            if rel.role == "main":
                main_artist = rel.artist
                break
        if not main_artist:
            rels = list(song.trackartist_set.all())
            if rels:
                main_artist = rels[0].artist
        if not main_artist:
            # اگر آرتیست موجود نیست، از لیست حذف
            continue

        artist_name = getattr(main_artist, "artistname", None)
        if not artist_name:
            continue

        # جمع‌بندی امتیاز
        score = (
            tw_score +
            velocity_score * 1.1 +
            growth_score * 0.75 +
            engagement_score * 0.9 +
            viral_score +
            session_score +
            completion_bonus -
            skip_penalty +
            freshness_score +
            decay_score +
            discovery_score +
            ai_score -
            manipulation_penalty +
            like_score
        )

        scored.append((score, song, artist_name))

    # مرتب‌سازی نزولی بر اساس امتیاز
    scored.sort(key=lambda x: x[0], reverse=True)

    # محدودیت per-artist (max 2 ترک از هر آرتیست)
    result = []
    counter = {}
    for score, song, name in scored:
        if counter.get(name, 0) >= 2:
            continue
        result.append(song)
        counter[name] = counter.get(name, 0) + 1
        if len(result) >= limit:
            break

    # ذخیره در کش
    cache.set(cache_key, result, timeout=cache_ttl)
    return result





def get_fresh_tracks(user=None, limit=20, cache_ttl=120):
    """
    Returns a list of 'fresh' tracks personalized per user.
    Cached uniquely per-user to avoid recomputation.
    Default cache TTL = 2 minutes.
    """

    # ایجاد کلید کش مخصوص هر کاربر
    user_key = getattr(user, "id", None) or "anon"
    cache_key = f"fresh_tracks_{user_key}_{limit}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now = timezone.now()
    min_date = now - timedelta(days=30)  # only 30-day-old tracks

    songs = (
        Songs.objects.filter(
            release_date__gte=min_date,
            is_published=True,
        )
        .select_related("genre")
        .prefetch_related(
            "trackartist_set",
            "trackartist_set__artist",
        )
    )

    # ----------------------------------
    # USER PROFILE
    # ----------------------------------
    user_genres = set()
    user_artists = set()

    if user and getattr(user, "is_authenticated", False):
        if hasattr(user, "favorite_genres"):
            user_genres = set(user.favorite_genres.values_list("id", flat=True))
        if hasattr(user, "favorite_artists"):
            user_artists = set(
                user.favorite_artists.values_list("artistname", flat=True)
            )

    scored = []

    # ----------------------------------
    # MAIN SCORING LOOP
    # ----------------------------------
    for song in songs:
        release_date = song.release_date
        days_old = (now - release_date).days if release_date else 0

        # 1️⃣ FRESHNESS
        freshness = exp(-days_old / 5)
        freshness_score = freshness * 40

        # 2️⃣ ENGAGEMENT
        total_seconds = song.total_listen_time or 0
        unique_listeners = song.unique_listeners or 0

        engagement_raw = log(total_seconds + 1) + log(unique_listeners + 1)
        engagement_score = min(engagement_raw * 3.5, 20)

        # 3️⃣ VELOCITY
        plays_last_day = song.plays_last_24h or 0
        velocity_score = min(log(plays_last_day + 1) * 6, 18)

        # 4️⃣ POPULARITY
        popularity_score = min(log(total_seconds + 1) * 1.5, 12)

        # 5️⃣ PERSONALIZATION
        interest_score = 0
        if song.genre_id in user_genres:
            interest_score += 10

        main_artist = None
        relations = song.trackartist_set.all()
        for rel in relations:
            if rel.role == "main":
                main_artist = rel.artist
                break
        if not main_artist and relations:
            main_artist = relations[0].artist

        artist_name = main_artist.artistname if main_artist else None

        if artist_name in user_artists:
            interest_score += 15

        # 6️⃣ EXPLORATION BOOST
        exploration_score = 0
        if days_old <= 7 and total_seconds < 50_000 and unique_listeners < 30:
            exploration_score = 6

        # 7️⃣ OVERPOPULARITY PENALTY
        diversity_penalty = -8 if total_seconds > 3_000_000 else 0

        # 8️⃣ NOISE (deterministic)
        noise = ((hash(song.id) % 100) / 100) * 0.8

        # FINAL SCORE
        score = (
            freshness_score * 1.0
            + engagement_score * 0.5
            + velocity_score * 0.6
            + popularity_score
            + interest_score
            + exploration_score
            + diversity_penalty
            + noise
        )

        scored.append((score, song, artist_name))

    # sort descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # ----------------------------------
    # LIMIT PER ARTIST
    # ----------------------------------
    result = []
    artist_counter = {}

    for score, song, artist_name in scored:
        if not artist_name:
            continue
        if artist_counter.get(artist_name, 0) >= 2:
            continue

        result.append(song)
        artist_counter[artist_name] = artist_counter.get(artist_name, 0) + 1

        if len(result) >= limit:
            break

    # ذخیره در کش (برای همه‌ی داده‌ها بر اساس یوزر)
    cache.set(cache_key, result, timeout=cache_ttl)

    return result


def fallback_mix(limit=20, user=None):
    songs = list(trending(limit))
    
    if len(songs) < limit:
        fresh_songs = get_fresh_tracks(user=user, limit=limit)
        
        # پیدا کردن ID آهنگ‌هایی که قبلا در لیست ترند بودند
        seen_ids = {s.id for s in songs}
        
        for s in fresh_songs:
            if s.id not in seen_ids:
                songs.append(s)
                seen_ids.add(s.id)
            
            if len(songs) >= limit:
                break
                
    return songs[:limit]
