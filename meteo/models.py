# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Meteo(models.Model):
    id = models.BigAutoField(primary_key=True)
    pressure = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    humidity = models.IntegerField(blank=True, null=True)
    processed_dttm = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'meteo'

    def __str__(self):
        return '{0} ℃, {1} mmHg, {2} %'.format(self.temperature, self.pressure, self.humidity)
