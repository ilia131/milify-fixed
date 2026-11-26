# Production deployment and credential rotation

Use `DJANGO_ENV=production`, an exact `DJANGO_ALLOWED_HOSTS` list, a long generated
`DJANGO_SECRET_KEY`, and the public HTTPS frontend origin in `DJANGO_FRONTEND_URL`.
Set `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` to the specific HTTPS browser origins.
Set `DJANGO_TRUST_PROXY=true` when the backend can only be reached through a trusted proxy
that overwrites `X-Forwarded-Proto`. The example Nginx TLS configuration binds upstreams
to loopback and overwrites the header. Review certificate paths and subdomain HTTPS
coverage before enabling long-lived HSTS. The Compose `proxy` profile is for HTTP
development only.

Apply migrations first on a staging database with a recent, controlled backup. The ad
migration preserves old counters and assigns zero to historical event charges. The wallet
migration retains prior balances and adds two fractional digits.

## Credential inventory from the prior redacted scan

Treat all access credentials below as compromised until the provider confirms revocation.
The prior run found 21 matches, including repeated exposures. Some findings were generic
and no service identity remained in the redacted match. Use the earlier privileged report
and provider inventory to reconcile them, without copying secret values into a ticket or Git.

| Credential | Affected service | Rotation |
| --- | --- | --- |
| Object storage access key pair | Arvan / S3-compatible storage | Issue a least-privilege pair for the application. Verify upload, private playback and download under that pair in staging, then revoke the exposed pair and review object-access logs. |
| Infrastructure access key pair | Liara | Create a new scoped deployment credential. Update the deployment secret store and validate a staging deployment. Revoke the exposed pair and examine activity. |
| Database password | PostgreSQL | Provision replacement application credentials with the same minimum grants. Switch connection pools and workers in staging, revoke the old password or role, and review login activity. |
| Django signing material | Django and JWT signing | Generate new signing material, distribute it consistently across workers, and require fresh sign-in. Avoid accepting compromised keys through fallback settings. Outstanding password reset links signed by the old key may also expire. |
| OAuth client secret | Google Cloud | Create a replacement for the configured OAuth client, update the secret store, validate the HTTPS origin and callback in staging, and disable the exposed secret. |
| SMTP password and API key | MailerOnline / SMTP transport | Reissue the application-specific password and API token, set both in their respective secret stores, send a staging reset message over STARTTLS, then revoke the old credentials. |
| VAPID private key | Web Push | Generate a new key pair, update server and client public configuration, re-register affected subscriptions, and retire the old key. |
| Tracked private key file | Purpose requires owner confirmation | Identify consumers by public fingerprint. Issue a replacement in the owning system and remove trust in the exposed key after cutover. |
| Unclassified generic matches | Owner review | Reconcile redacted findings from historical `.env`, `backend/settings.py`, and `backend/production.txt` with the provider inventory. Rotate any active credential discovered. |

## Arvan access controls

Ensure anonymous reads of existing subscription-only audio and paid `beats/files/`
objects are denied individually by the provider policy. Public free audio, images and
previews may use their existing public URLs. The API issues 15-minute signed URLs after
verifying entitlement for private audio. A signed URL alone does not make an existing
public object private. Check anonymous and signed requests against owner-provided staging
objects before deployment. No live policy was changed during this work.

## Advertising accounting

The platform's UI uses toman (IRT). CPM bills the price divided by 1,000 per new
impression, CPC bills the price per new click, and CPV bills the price once when a
video with a known duration is reported complete at 100% and reaches the configured
duration. Charges retain seven decimal places and reserve funds against the campaign
budget under a PostgreSQL lock. Admin statistics include the recorded charges in the
selected date range. Historical reports preserve their event counts.

This release records campaign spend. The advertiser model has no funded-wallet
relationship and the repository has no verified billing-provider sandbox. No
advertiser balance is debited by these events. Client playback reports still need
independent fraud controls for billing that moves real funds.
