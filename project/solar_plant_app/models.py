from django.db import models


class Plant(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)


class Datapoint(models.Model):
    class Meta:
        unique_together = (('plant', 'timestamp'),)

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='datapoint')
    timestamp = models.DateTimeField(null=False)
    energy_expected = models.FloatField(null=False)
    energy_observed = models.FloatField(null=False)
    irradiation_expected = models.FloatField(null=False)
    irradiation_observed = models.FloatField(null=False)
