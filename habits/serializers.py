from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    # делаем вознаграждение необязательным и допускаем пустую строку,
    # чтобы можно было использовать только связанную привычку
    reward = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time_moment",
            "action",
            "is_pleasant",
            "linked_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
        ]
        read_only_fields = ["user"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        def get_value(name, default=None):
            if name in attrs:
                return attrs[name]
            if instance is not None:
                return getattr(instance, name)
            return default

        reward = get_value("reward")
        linked_habit = get_value("linked_habit")
        is_pleasant = get_value("is_pleasant", False)
        duration = get_value("duration")
        periodicity = get_value("periodicity")

        errors = {}

        if reward and linked_habit:
            errors["reward"] = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["linked_habit"] = "Нельзя одновременно указывать вознаграждение и связанную привычку."

        if is_pleasant and (reward or linked_habit):
            errors["is_pleasant"] = "У приятной привычки не может быть вознаграждения или связанной привычки."

        if duration is not None:
            total_seconds = duration.hour * 3600 + duration.minute * 60 + duration.second
            if total_seconds > 120:
                errors["duration"] = "Время выполнения не может быть больше 120 секунд."

        if linked_habit and not linked_habit.is_pleasant:
            errors["linked_habit"] = "Связанной привычкой может быть только привычка с признаком приятной."

        if periodicity:
            days = None
            text = str(periodicity).strip().lower()

            if text.isdigit():
                days = int(text)
            elif text in {"ежедневная", "каждый день"}:
                days = 1
            elif text in {"еженедельная", "раз в неделю"}:
                days = 7

            if days is not None and days > 7:
                errors["periodicity"] = "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
