from django.urls import path

from .views import GameListCreateAPIView,GameRetrieveUpdateDestroyAPIView, upload_game, home, ranking

app_name = "game"
urlpatterns = [
    path("", home, name="home"),
    path("upload-game", upload_game, name="upload_game"),
    path("ranking-table", ranking, name="ranking_table"),
    path('api/games/', GameListCreateAPIView.as_view(), name='game-list'),
    path('api/games/<int:pk>/', GameRetrieveUpdateDestroyAPIView.as_view(), name='game-detail'),
]
