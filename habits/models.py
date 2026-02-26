from django.db import models


class Habit(models.Model):
    user = models.ForeignKey("user.User", verbose_name="создатель", on_delete=models.CASCADE)
    place = models.CharField(max_length=120, verbose_name="место привычки")
    time_moment = models.TimeField(verbose_name="время привычки")
    action = models.TextField(verbose_name="действие привычки")
    is_pleasant = models.BooleanField(default=False, verbose_name="признак приятной привычки")
    linked_habit = models.ForeignKey('habits.Habit', verbose_name='свяазанная привычка', on_delete=models.CASCADE, null=True, blank=True)
    periodicity = models.TextField(verbose_name='периодичность привычки', default="ежедневная")
    reward = models.TextField(verbose_name="вознаграждение")
    duration = models.TimeField(verbose_name="время на выполнение привычки")
    is_public = models.BooleanField(default=False, verbose_name="публичность")
