# views.py

import tablib
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .resources import GameResource


def home(request):
    return render(request, "home.html")


@csrf_exempt
def upload_game(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        resource = GameResource()
        try:
            dataset = tablib.Dataset().load(
                csv_file.read().decode("utf-8"), format="csv", delimiter=",", headers=False
            )
            dataset.headers = [
                "home_team",
                "home_team_score",
                "away_team",
                "away_team_score",
            ]
            dataset.insert_col(0, col=lambda x: "", header="id")
            result = resource.import_data(dataset, dry_run=False)
            messages.success(request, "Games uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error uploading games: {e}")

    return render(request, "upload_game.html")
