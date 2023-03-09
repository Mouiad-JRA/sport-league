import tablib
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm
from .models import Team, Game
from .resources import GameResource
from .serializers import GameSerializer
from .strategies import AlternateRankingStrategy, BasicRankingStrategy


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("game:home")

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(error)
        context = {
            "form": form,
            "errors": error_messages,
        }
        return render(self.request, self.template_name, context)

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(email=email, password=password)
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    template_name = "registration/login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("game:home")

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(error)
        context = {
            "form": form,
            "errors": error_messages,
        }
        return render(self.request, self.template_name, context)
    def form_valid(self, form):
        email = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class LogoutView(RedirectView):
    url = reverse_lazy("game:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


def home(request):
    return render(request, "home.html")


@login_required
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
            return redirect(reverse("game:ranking_table"))
        except Exception as e:
            messages.error(request, f"Error uploading games: {e}")

    return render(request, "upload_game.html")


@login_required
def ranking(request):
    strategy = BasicRankingStrategy()
    if 'ranking_strategy' in request.POST:
        if request.POST['ranking_strategy'] == 'alternate':
            strategy = AlternateRankingStrategy()

    teams = Team.objects.all()
    games = Game.objects.all()
    standings = strategy.calculate_rankings(teams)

    if request.is_ajax():
        return render(request, 'ranking_table.html', {'standings': standings, 'games': games})

    return render(request, 'ranking_table_page.html', {'standings': standings, 'games': games})


class GameListCreateAPIView(APIView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        game = self.get_object(pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def put(self, request, pk):
        game = self.get_object(pk)
        serializer = GameSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        game = self.get_object(pk)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
