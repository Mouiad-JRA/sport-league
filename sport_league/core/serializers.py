from rest_framework import serializers

from .models import Game, Team


class TeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField()  # To remove the unique validator check

    class Meta:
        model = Team
        fields = ["id", "name"]


class GameSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(required=False)
    away_team = TeamSerializer(required=False)

    class Meta:
        model = Game
        fields = ["id", "home_team", "home_team_score", "away_team", "away_team_score"]

    def validate(self, attrs):
        if not self.instance:
            errors = {}
            if not attrs.get("home_team"):
                errors["home_team"] = ["This field is required"]
            if not attrs.get("away_team"):
                errors["home_team"] = ["This field is required"]
        return attrs

    def create(self, validated_data):
        home_team_data = validated_data.pop("home_team")
        away_team_data = validated_data.pop("away_team")
        home_team, created = Team.objects.get_or_create(**home_team_data)
        away_team, created = Team.objects.get_or_create(**away_team_data)
        validated_data["home_team"] = home_team
        validated_data["away_team"] = away_team
        game = super(GameSerializer, self).create(validated_data)
        return game

    def update(self, instance, validated_data):
        home_team_data = validated_data.pop("home_team", {})
        away_team_data = validated_data.pop("away_team", {})
        # we won't allow to edit teams for now
        # but if we want we need to know do we need to change the team name or just change the team itself
        instance = super(GameSerializer, self).update(instance, validated_data)
        return instance
