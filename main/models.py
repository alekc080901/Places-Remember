from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(models.Model):
    uid = models.PositiveIntegerField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    avatar = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Memory(models.Model):
    user = models.PositiveIntegerField()
    latitude = models.FloatField()
    zoom = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(18)])
    longitude = models.FloatField()
    place = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.place
