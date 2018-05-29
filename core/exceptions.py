from rest_framework.exceptions import APIException

class CardInvalid(APIException):
    """
    Raises when submitted card information is invalid.
    """
    status_code = 400
    default_code = 'card_invalid'
    default_detail = 'Card invalid.'

class AlreadyVoted(APIException):
    """
    Raises when the elector has already voted.
    """
    status_code = 401
    default_code = 'already_voted'
    default_detail = 'Elector has already voted.'

class ElectorSuspicious(APIException):
    """
    Raises when elector is considered suspicious and the request is denied.
    """
    status_code = 401
    default_code = 'elector_suspicious'
    default_detail = 'Elector is considered suspicious due to information mismatch.'

class ElectorBanned(APIException):
    """
    Raises when the elector is banned from the current election.
    """
    status_code = 401
    default_code = 'elector_banned'
    default_detail = 'Elector is banned from this election.'

class NotQualified(APIException):
    """
    Raises when the elector is not qualified to vote on any ballots in this election.
    """
    status_code = 401
    default_code = 'not_qualified'
    default_detail = 'Elector isn’t qualified to vote in this election.'

class SessionInvalid(APIException):
    status_code = 403
    default_code = 'session_invalid'
    default_detail = 'Session invalid.'
