# Response entities
from . import meta

class StudentInfo(object):
    """
    Contains student information acquired from ACA.
    """

    def __init__(self, id=None, type=None, valid=False, college=None, department=None, entity=None):
        self.id = id or entity['stuid']
        self.type = type or entity['stutype']  # Mandarin value returned from ACA server
        self.valid = valid or (entity['incampus'] == 'true')
        self.college = college or entity['college']
        self.department = department or entity['dptcode']

    def __repr__(self):
        return "{0}(id='{id}', type='{type}', valid={valid}, college='{college}', department='{department}')".format(self.__class__.__name__, **self.__dict__)

    def __str__(self):
        return '<StudentInfo: {id} ({college} {type} {department}){0}>'.format('' if self.valid else '*', **self.__dict__)

    @property
    def college_id(self):
        """
        Returns the normalized college ID or `None` if not known.
        """
        return meta.COLLEGE_IDS.get(self.college)
