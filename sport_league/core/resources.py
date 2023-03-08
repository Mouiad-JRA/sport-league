from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from .models import Game, Team


class GameResource(resources.ModelResource):
    home_team = Field(
        column_name="home_team",
        attribute="home_team",
        widget=ForeignKeyWidget(Team, "name"),
    )
    away_team = Field(
        column_name="away_team",
        attribute="away_team",
        widget=ForeignKeyWidget(Team, "name"),
    )

    class Meta:
        model = Game
        fields = ("id", "home_team", "home_team_score", "away_team", "away_team_score")

    def before_import_row(self, row, **kwargs):
        home_team_name = row["home_team"]
        away_team_name = row["away_team"]
        Team.objects.get_or_create(name=home_team_name)
        Team.objects.get_or_create(name=away_team_name)
