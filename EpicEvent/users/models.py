from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import PermissionDenied

MANAGEMENT = "MANAGEMENT"
SALES = "SALES"
SUPPORT = "SUPPORT"

TEAM_LIMIT = 3


class Team(models.Model):

    name = models.CharField(max_length=10,
                            choices=((MANAGEMENT, "Management"), (SALES, "Sales"), (SUPPORT, "Support")))
    objects = models.Manager()

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        # Prevent from deleting teams.
        raise PermissionDenied(detail="You are not permitted to delete teams.")


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return f"{self.username} ({self.team.name})"

    def save(self, *args, **kwargs):
        if self.team.name == MANAGEMENT:
            self.is_superuser = True
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False

        user = super(User, self)
        user.save()

        return user
