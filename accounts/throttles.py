from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
)


class SupportAnonRateThrottle(AnonRateThrottle):

    scope = "support_anon"


class SupportUserRateThrottle(UserRateThrottle):

    scope = "support_user"