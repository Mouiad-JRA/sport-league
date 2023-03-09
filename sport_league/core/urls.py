from django.urls import path

from .views import GameListCreateAPIView, GameRetrieveUpdateDestroyAPIView, upload_game, ranking, \
    RegisterView, LoginView, home, LogoutView

app_name = "game"
urlpatterns = [
    path("", home, name="home"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path("upload-game", upload_game, name="upload_game"),
    path("ranking-table", ranking, name="ranking_table"),
    path('api/games/', GameListCreateAPIView.as_view(), name='game-list'),
    path('api/games/<int:pk>/', GameRetrieveUpdateDestroyAPIView.as_view(), name='game-detail'),
]
