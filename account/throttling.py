import logging
from rest_framework.throttling import AnonRateThrottle

logger = logging.getLogger('vote.auth')

class StrictAnonRateThrottle(AnonRateThrottle):
    """
    Limits the rates of API calls for sensitive endpoints.
    """
    scope = 'strict'

    def throttle_failure(self):
        logger.warning('Reached throttle threshold')
        return super().throttle_failure()
