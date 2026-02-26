import os
import requests
from celery import shared_task
from django.utils import timezone

from .models import Habit


BOT_TOKEN = os.getenv("BOT_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" if BOT_TOKEN else None


def send_telegram_message(chat_id: str, text: str) -> None:
    if not TELEGRAM_API_URL or not chat_id:
        return

    try:
        requests.post(
            TELEGRAM_API_URL,
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception:
        pass


@shared_task
def send_habit_reminders() -> None:
    now = timezone.now()
    current_time = now.time().replace(second=0, microsecond=0)

    habits = (
        Habit.objects.filter(time_moment=current_time)
        .select_related("user")
    )

    for habit in habits:
        user = habit.user
        chat_id = getattr(user, "telegram_chat_id", None)
        if not chat_id:
            continue

        text = (
            f"Напоминание о привычке:\n"
            f"- действие: {habit.action}\n"
            f"- место: {habit.place}\n"
            f"- время: {habit.time_moment.strftime('%H:%M')}"
        )
        send_telegram_message(chat_id, text)
