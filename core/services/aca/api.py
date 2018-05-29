import logging
from ..errors import ExternalError
from .entities import StudentInfo
from .protocol import AcaRequest
from .utils import raise_exception, reverse_indian

logger = logging.getLogger('vote.aca')

def query_student(student_id_with_rev):
    """
    Gets the relevant student information from ACA.
    """
    # Loads the response from ACA
    request = AcaRequest(stuid=student_id_with_rev)
    response = request.post('stuinfo2ByStuId')

    # Read the response entity
    try:
        if not response.ok:
            error = response.error
            logger.warning('Querying ACA failed: %s', error)
            raise_exception(error)  # NOTE: Should we record mismatched revision?
        info = StudentInfo(entity=response)
    except KeyError:
        logger.exception('Server entity malformed')
        raise ExternalError(code='entity_malformed')

    logger.info(str(info))
    return info


def to_student_id(internal_id):
    """
    Gets the student ID and relevant information associated with this card from ACA.
    """
    # Build the request
    serial_id = str(reverse_indian(int(internal_id, 16))[0])
    request = AcaRequest(cardno=serial_id)

    # Load and parse response
    response = request.post('stuinfo2ByCardno')

    # Read the response entity
    try:
        if not response.ok:
            error = response.error
            logger.warning('Querying ACA failed: %s', error)
            raise_exception(error)
        info = StudentInfo(entity=response)
    except KeyError:
        logger.exception('Server entity malformed')
        raise ExternalError(code='entity_malformed')

    logger.info(str(info))
    return info
