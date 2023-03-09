import pytest
from django.test import TestCase

from core.models import Team, Game


class TestGame(TestCase):

    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.game = Game.objects.create(home_team=self.team1, home_team_score=2, away_team=self.team2,
                                        away_team_score=1)

    def tearDown(self):
        self.team1.delete()
        self.team2.delete()
        self.game.delete()

    def test_is_draw(self):
        self.game.home_team_score = 1
        self.game.away_team_score = 1
        self.game.save()
        assert self.game.is_draw() == True

    def test_is_winner(self):
        assert self.game.is_winner(self.team1) == True
        assert self.game.is_winner(self.team2) == False

    def test_winner_team(self):
        self.game.home_team_score = 1
        self.game.away_team_score = 1
        self.game.save()
        assert self.game.winner_team is None

        self.game.home_team_score = 3
        self.game.away_team_score = 1
        self.game.save()
        assert self.game.winner_team == self.team1

        self.game.home_team_score = 1
        self.game.away_team_score = 3
        self.game.save()
        assert self.game.winner_team == self.team2


class TestTeam(TestCase):

    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.game = Game.objects.create(home_team=self.team1, home_team_score=2, away_team=self.team2,
                                        away_team_score=1)

    def tearDown(self):
        self.team1.delete()
        self.team2.delete()
        self.game.delete()

    def test_team_str(self):
        assert str(self.team1) == "Team 1"
        assert str(self.team2) == "Team 2"

    def test_team_games(self):
        assert self.team1.games.count() == 1
        assert self.team2.games.count() == 1

        # Add a new game and make sure it's counted in the team's games
        new_game = Game.objects.create(home_team=self.team1, home_team_score=3, away_team=self.team2, away_team_score=2)
        assert self.team1.games.count() == 2
        assert self.team2.games.count() == 2
        new_game.delete()
