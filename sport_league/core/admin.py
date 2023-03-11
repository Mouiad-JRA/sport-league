from django.contrib import admin

from .models import Game, Team, User

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Team)
