from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and
        password.
        """
        if not email:
            raise ValueError(_("The given email must be set"))

        email = UserManager.normalize_email(email)

        user = self.model(
            email=email,
            is_active=True,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email"), max_length=255, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.get_full_name() + "  " + self.email


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name if self.name else ""

    @property
    def games(self):
        return self.home_games.all() | self.away_games.all()


class Game(models.Model):
    home_team = models.ForeignKey(
        Team, related_name="home_games", on_delete=models.CASCADE
    )
    home_team_score = models.PositiveIntegerField()
    away_team = models.ForeignKey(
        Team, related_name="away_games", on_delete=models.CASCADE
    )
    away_team_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.home_team}:{self.home_team_score}--{self.away_team}:{self.away_team_score}"

    def is_draw(self):
        return self.away_team_score == self.home_team_score

    def is_winner(self, team):
        return self.winner_team == team

    @property
    def winner_team(self):
        if self.is_draw():
            return None

        if self.home_team_score > self.away_team_score:
            return self.home_team

        return self.away_team
