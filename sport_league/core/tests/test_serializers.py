from core.models import Team
from core.serializers import TeamSerializer
from django.test import TestCase


class TeamSerializerTestCase(TestCase):
    def setUp(self):
        self.team_data = {"name": "Manchester United"}
        self.team = Team.objects.create(name="Chelsea")

    def tearDown(self):
        self.team.delete()

    def test_valid_data(self):
        serializer = TeamSerializer(data=self.team_data)
        self.assertTrue(serializer.is_valid())
        team = serializer.save()
        self.assertEqual(team.name, self.team_data["name"])

    def test_blank_name(self):
        self.team_data["name"] = ""
        serializer = TeamSerializer(data=self.team_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {"name"})
        self.assertEqual(
            str(serializer.errors["name"][0]), "This field may not be blank."
        )
