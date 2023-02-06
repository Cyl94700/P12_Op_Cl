from django.contrib.auth.models import AbstractUser
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=10)


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return f"{self.username} ({self.team.name})"
