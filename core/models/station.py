from django.db import models

class Station(models.Model):
    """
    Represents a voting station.
    """

    # The election associated with this ballot
    election = models.ForeignKey('Election', on_delete=models.CASCADE)

    # Station ID in vote system
    foreign_id = models.IntegerField()

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
