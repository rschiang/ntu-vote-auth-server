import re
import logging
import struct
from collections import OrderedDict
from django.db.models.query import QuerySet
from django.conf import settings
from urllib.request import Request, urlopen
from xml.etree import ElementTree as et

logger = logging.getLogger('vote.service')


def reverse_indian(i):
    return struct.unpack('<I', struct.pack('>I', i))


def to_student_id(internal_id):
    # Build up the clumsy request entity
    req_entity = et.Element('STUREQ')
    req_uid = et.SubElement(req_entity, 'UID')
    req_uid.text = settings.ACA_API_USER
    req_pass = et.SubElement(req_entity, 'PASSWORD')
    req_pass.text = settings.ACA_API_PASSWORD
    req_cid = et.SubElement(req_entity, 'CARDNO')
    req_cid.text = str(reverse_indian(int(internal_id, 16))[0])
    req_data = et.tostring(req_entity, encoding='big5')

    # Initiate HTTP request
    request = Request(settings.ACA_API_URL, method='POST')
    request.add_header('Content-Type', 'application/xml')
    request.add_header('X-Requested-With', 'NTUVote')

    # Load and parse response
    try:
        response = urlopen(request, data=req_data)
        resp_data = response.read().decode('big5')
        resp_entity = et.fromstring(resp_data)
    except (UnicodeDecodeError, et.ParseError):
        logger.exception('Failed to load server entity')
        raise ExternalError('entity_malformed')

    # Read the response entity
    try:
        status = resp_entity.find('WEBOK').text
        error = resp_entity.find('ERROR').text

        if status != 'OK':
            logger.warning('Querying ACA failed: %s', error)

            if '為黑名單' in error:
                raise ExternalError('card_blacklisted')
            elif '在卡務中不存在' in error or '尚未啟用' in error:
                raise ExternalError('card_invalid')
            elif '查無學號資料' in error:
                raise ExternalError('student_not_found')
            elif '未授權' in error:
                raise ExternalError('unauthorized')
            elif '輸入資料錯誤' in error:
                raise ExternalError('params_invalid')

            # All other rare cases
            raise ExternalError(error)

        info = StudentInfo()
        info.id = resp_entity.find('STUID').text
        info.type = resp_entity.find('STUTYPE').text
        info.valid = resp_entity.find('INCAMPUS').text
        info.college = resp_entity.find('COLLEGE').text
        info.department = resp_entity.find('DPTCODE').text

    except AttributeError:
        logger.exception('Server entity malformed')
        raise ExternalError('entity_malformed')

    # Normalize
    info.valid = (info.valid == 'true')

    logger.info(str(info))
    return info


class StudentInfo(object):

    def __init__(self, id=None, type=None, valid=False, college=None, department=None):
        self.id = id
        self.type = type
        self.valid = valid
        self.college = college
        self.department = department

    def __repr__(self):
        return "{0}(id='{id}', type='{type}', valid={valid}, college='{college}', department='{department}')".format(self.__class__.__name__, **self.__dict__)

    def __str__(self):
        return '<StudentInfo: {id} ({college} {type} {department}){0}>'.format('' if self.valid else '*', **self.__dict__)


class ExternalError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class BaseEntryRule(object):
    queryset = None

    target_department = None

    lookup_field = None
    lookup_info_kwarg = None
    entry_field = None

    def get_queryset(self):
        """
        Get list of entry for this rule.
        This must be iterable, and maybe a queryset.
        Defaults to use `self.queryset`

        You may want to override this, if you need to provide
        different querysets depending on the income.
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def get_object(self, student_info):
        # Apply department filter (regular expression)
        if self.target_department is not None:
            if re.match(self.target_department, student_info.department) is None:
                return None
        return self.get_kind(student_info)

    def get_kind(self, student_info):
        """
        return kinds related to @student_info, and it returns None if the student
        does not be accepted by rule. All rule class should follow this criterion.
        """
        try:
            filter_kwargs = {
                self.lookup_field: getattr(student_info, self.lookup_info_kwarg)
            }
            obj = self.get_queryset().get(**filter_kwargs)
            return getattr(obj, self.entry_field)
        except:
            return None


class KindiClassifier(object):
    # TODO: read seettings from config
    entry_rule_classes = OrderedDict()

    def get_kind(self, student_info):
        """
        Evaluate each entry rule in the list, and use the first
        non-None value as final result.
        """
        er_classes = [er_class() for er_class in self.entry_rule_classes.values()]
        entrys = [er_class.get_object(student_info) for er_class in er_classes]
        # return the first non-None value or None
        kind = next((entry for entry in entrys if entry is not None), None)
        return kind

    def register(self, name, entry_rule):
        if name not in self.entry_rule_classes:
            self.entry_rule_classes[name] = entry_rule

    def unregister(self, name):
        if name not in self.entry_rule_classes:
            raise ValueError('{} Not found'.format(name))
        del self.entry_rule_classes[name]


# Global instance of entry providor
kind_classifier = KindiClassifier()
