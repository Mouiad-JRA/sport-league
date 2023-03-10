from core.models import Game, Team
from core.serializers import GameSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class UploadGameViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("game:upload_game")

    def test_upload_game_valid_csv(self):
        data = b"Team A,2,Team B,1\nTeam C,3,Team D,1\n"
        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game:ranking_table"))
        self.assertEqual(Game.objects.count(), 2)

    def test_upload_game_invalid_csv(self):
        data = b"Team A,2,Team B\nTeam C,3,Team D,1\n"
        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 0)

    def test_upload_game_no_file(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 0)


class TestRankingView(TestCase):
    def setUp(self):
        self.client = APIClient()

        Team.objects.create(name="Barcelona")
        Team.objects.create(name="Real Madrid")

        Game.objects.create(
            home_team=Team.objects.get(name="Barcelona"),
            home_team_score=2,
            away_team=Team.objects.get(name="Real Madrid"),
            away_team_score=1,
        )
        Game.objects.create(
            home_team=Team.objects.get(name="Real Madrid"),
            home_team_score=3,
            away_team=Team.objects.get(name="Barcelona"),
            away_team_score=2,
        )

    def tearDown(self):
        Game.objects.all().delete()
        Team.objects.all().delete()

    def test_basic_ranking_strategy(self):
        url = reverse("game:ranking_table")
        response = self.client.get(url, {"ranking_strategy": "basic"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context["standings"]), 2)
        self.assertEqual(response.context["standings"][0][0].name, "Barcelona")
        self.assertEqual(response.context["standings"][0][1], 3)

    def test_alternate_ranking_strategy(self):
        url = reverse("game:ranking_table")
        response = self.client.get(url, {"ranking_strategy": "alternate"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context["standings"]), 2)
        self.assertEqual(response.context["standings"][0][0].name, "Barcelona")
        self.assertEqual(response.context["standings"][0][1], 3)


class GameListCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.game = Game.objects.create(
            home_team=self.team1,
            away_team=self.team2,
            home_team_score=2,
            away_team_score=1,
        )
        self.valid_payload = {
            "home_team": {"name": "Team 3"},
            "home_team_score": 3,
            "away_team": {"name": "Team 4"},
            "away_team_score": 0,
        }
        self.invalid_payload = {
            "home_team": {"name": ""},
            "home_team_score": -1,
            "away_team": {"name": ""},
            "away_team_score": 0,
        }

    def tearDown(self):
        self.team1.delete()
        self.team2.delete()
        self.game.delete()

    def test_get_all_games(self):
        url = reverse("game:game-list")
        response = self.client.get(url)
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_game(self):
        url = reverse("game:game-list")
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

    def test_create_invalid_game(self):
        url = reverse("game:game-list")
        response = self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GameRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.game = Game.objects.create(
            home_team=Team.objects.create(name="Team A"),
            away_team=Team.objects.create(name="Team B"),
            home_team_score=1,
            away_team_score=2,
        )
        self.valid_payload = {
            "home_team": {"name": "Team A"},
            "away_team": {"name": "Team B"},
            "home_team_score": 3,
            "away_team_score": 2,
        }
        self.invalid_payload = {
            "home_team": {"name": "Team A"},
            "away_team": {"wrong": 1},
            "home_team_score": 3,
            "away_team_score": 2,
        }

    def test_retrieve_game(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["home_team"]["name"], "Team A")
        self.assertEqual(response.data["away_team"]["name"], "Team B")
        self.assertEqual(response.data["home_team_score"], 1)
        self.assertEqual(response.data["away_team_score"], 2)

    def test_update_game_with_valid_payload(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        response = self.client.put(url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["home_team"]["name"], "Team A")
        self.assertEqual(response.data["away_team"]["name"], "Team B")
        self.assertEqual(response.data["home_team_score"], 3)
        self.assertEqual(response.data["away_team_score"], 2)

    def test_update_game_with_invalid_payload(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        response = self.client.put(url, data=self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_game(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())
