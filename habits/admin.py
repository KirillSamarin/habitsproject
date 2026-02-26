from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["user"]
    search_fields = ["user"]
