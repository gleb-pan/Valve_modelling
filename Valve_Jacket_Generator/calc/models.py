from django.db import models

# Create your models here.


class ValveParams(models.Model):
    flange_c = models.CharField(max_length=10)
    flange_thck = models.CharField(max_length=10)
    shield_c = models.CharField(max_length=10)
    pipe_c = models.CharField(max_length=10)
    valve_c = models.CharField(max_length=10)
    valve_l = models.CharField(max_length=10)
    gap_left = models.CharField(max_length=10)
    gap_right = models.CharField(max_length=10)
    X_offset = models.CharField(max_length=10)
    Y_offset = models.CharField(max_length=10)
    hole_offset = models.CharField(max_length=10)
