# # music/tasks.py

# from celery import shared_task

# from django.core.cache import cache
# from django_redis import get_redis_connection

# from music.models import Songs
# from artists.models import Artist


# redis_conn = get_redis_connection("default")


# @shared_task
# def sync_stats_from_redis():

#     # --------------------------------
#     # Songs
#     # --------------------------------

#     songs = Songs.objects.all()

#     for song in songs:

#         play_count = cache.get(
#             f"song:{song.id}:play_count"
#         )

#         listen_time = cache.get(
#             f"song:{song.id}:listen_time"
#         )

#         plays_24h = cache.get(
#             f"song:{song.id}:plays_24h"
#         )

#         unique_listener_key = (
#             f"song:{song.id}:unique_listeners"
#         )

#         unique_listeners = redis_conn.scard(
#             unique_listener_key
#         )

#         update_data = {}

#         if play_count is not None:
#             update_data["play_count"] = int(play_count)

#         if listen_time is not None:
#             update_data["total_listen_time"] = int(listen_time)

#         if plays_24h is not None:
#             update_data["plays_last_24h"] = int(plays_24h)

#         update_data["unique_listeners"] = int(unique_listeners)

#         if update_data:

#             Songs.objects.filter(
#                 id=song.id
#             ).update(**update_data)

#     # --------------------------------
#     # Artists
#     # --------------------------------

#     artists = Artist.objects.all()

#     for artist in artists:

#         monthly_key = (
#             f"artist:{artist.id}:monthly_listeners"
#         )

#         monthly_listeners = redis_conn.scard(
#             monthly_key
#         )

#         Artist.objects.filter(
#             id=artist.id
#         ).update(
#             monthly_listeners=int(monthly_listeners)
#         )
