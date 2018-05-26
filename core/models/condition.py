from django.db import models

class Condition(models.Model):
    """
    Represents the conditions of ballot eligibility in a tree structure.
    """

    MATCH_ALL = 'ALL'
    MATCH_ANY = 'ANY'

    # The ballot associated with this condition
    ballot = models.ForeignKey('Ballot', on_delete=models.CASCADE, related_name='conditions')

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children')
    field = models.CharField(max_length=12)
    value = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return 'Match {field} = {value}'.format(**self.__dict__)

    def match(self, fields, queryset=None):
        """
        Returns if the given fields satisfy this condition.
        """
        if queryset:    # Use cached queryset if available
            children = queryset.filter(parent=self)
        else:
            children = self.children.all()

        if self.field == Condition.MATCH_ALL:
            return all(i.match(fields, queryset=queryset) for i in children)
        elif self.field == Condition.MATCH_ANY:
            return any(i.match(fields, queryset=queryset) for i in children)
        else:
            return fields.get(self.field) == self.value
