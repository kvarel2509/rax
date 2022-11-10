from .forms import FavoriteColorAdminForm
from .models import FavoriteColor

from django.contrib import admin


@admin.register(FavoriteColor)
class FavoriteColorAdmin(admin.ModelAdmin):
	form = FavoriteColorAdminForm
