from django.urls import path

from .views import (
    HabitCreateView,
    HabitDeleteView,
    HabitDetailView,
    HabitListView,
    HabitUpdateView,
    PublicHabitListView,
)

urlpatterns = [
    path("", HabitListView.as_view(), name="habit-list"),
    path("create/", HabitCreateView.as_view(), name="habit-create"),
    path("public/", PublicHabitListView.as_view(), name="habit-public-list"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit-detail"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habit-update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit-delete"),
]
