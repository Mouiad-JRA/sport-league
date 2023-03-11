from core.models import Game, Team
from core.serializers import GameSerializer
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("game:register")
        self.valid_data = {
            "email": "testuser@example.com",
            "password1": "Momohanaj2mf!",
            "password2": "Momohanaj2mf!",
        }
        self.invalid_data = {
            "email": "invalidemail",
            "password1": "Momohanaj2mf!",
            "password2": "Momohanaj2mf21",
        }

    def test_register_with_valid_data(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, reverse("game:home"))
        user = User.objects.get(email=self.valid_data["email"])
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.valid_data["password1"]))

    def test_register_with_invalid_data(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn("email", form.errors)
        self.assertIn("password2", form.errors)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("game:login")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="Momohanaj2mf!"
        )
        self.valid_data = {"username": self.user.email, "password": "Momohanaj2mf!"}
        self.invalid_data = {"username": self.user.email, "password": "wrongpassword"}

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, reverse("game:home"))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email and password.")


class UploadGameViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("game:upload_game")
        user = User.objects.create_user("testuser", "testuser@example.com")
        user.set_password("Momohanaj2mf!")
        user.save()

    def test_upload_game_valid_csv(self):
        data = b"Team A,2,Team B,1\nTeam C,3,Team D,1\n"
        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        self.client.login(username="testuser", password="Momohanaj2mf!")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game:ranking_table"))
        self.assertEqual(Game.objects.count(), 2)

    def test_upload_game_invalid_csv(self):
        data = b"Team A,2,Team B\nTeam C,3,Team D,1\n"

        self.client.login(username="testuser", password="Momohanaj2mf!")

        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 0)

    def test_upload_game_no_file(self):
        response = self.client.post(self.url)
        self.client.login(username="testuser", password="Momohanaj2mf!")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Game.objects.count(), 0)


class TestRankingView(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user("testuser", "testuser@example.com")
        user.set_password("Momohanaj2mf!")
        user.save()

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
        User.objects.all().delete()

    def test_basic_ranking_strategy(self):
        url = reverse("game:ranking_table")
        self.client.login(username="testuser", password="Momohanaj2mf!")
        response = self.client.get(url, {"ranking_strategy": "basic"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context["standings"]), 2)
        self.assertEqual(response.context["standings"][0][0].name, "Barcelona")
        self.assertEqual(response.context["standings"][0][1], 3)

    def test_alternate_ranking_strategy(self):
        url = reverse("game:ranking_table")
        self.client.login(username="testuser", password="Momohanaj2mf!")
        response = self.client.get(url, {"ranking_strategy": "alternate"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context["standings"]), 2)
        self.assertEqual(response.context["standings"][0][0].name, "Barcelona")
        self.assertEqual(response.context["standings"][0][1], 3)


class GameListCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "testuser@example.com")
        self.user.set_password("Momohanaj2mf!")
        self.user.save()
        self.client.force_authenticate(user=self.user)
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
        self.user.delete()
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

    def test_game_list_create_api_view_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse("game:game-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GameRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "testuser@example.com")
        self.user.set_password("Momohanaj2mf!")
        self.user.save()
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
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["home_team"]["name"], "Team A")
        self.assertEqual(response.data["away_team"]["name"], "Team B")
        self.assertEqual(response.data["home_team_score"], 1)
        self.assertEqual(response.data["away_team_score"], 2)

    def test_update_game_with_valid_payload(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["home_team"]["name"], "Team A")
        self.assertEqual(response.data["away_team"]["name"], "Team B")
        self.assertEqual(response.data["home_team_score"], 3)
        self.assertEqual(response.data["away_team_score"], 2)

    def test_update_game_with_invalid_payload(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data=self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_game(self):
        url = reverse("game:game-detail", args=[self.game.pk])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())
