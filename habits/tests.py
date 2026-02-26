from datetime import time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Habit
from .tasks import send_habit_reminders


User = get_user_model()


class HabitAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="strongpass123",
            username="owner",
            telegram_chat_id="111111",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_habit_for_current_user(self):
        url = "/api/habits/create/"
        data = {
            "place": "дом",
            "time_moment": "08:00:00",
            "action": "делать зарядку",
            "is_pleasant": False,
            "linked_habit": None,
            "periodicity": "ежедневная",
            "reward": "кофе",
            "duration": "00:02:00",
            "is_public": True,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(id=response.data["id"])
        self.assertEqual(habit.user, self.user)

    def test_user_sees_only_own_habits_in_list(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="strongpass123",
            username="other",
        )
        Habit.objects.create(
            user=self.user,
            place="дом",
            time_moment=time(9, 0),
            action="чтение",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="чай",
            duration=time(0, 2, 0),
            is_public=False,
        )
        Habit.objects.create(
            user=other_user,
            place="офис",
            time_moment=time(10, 0),
            action="кофе-брейк",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="печенье",
            duration=time(0, 2, 0),
            is_public=False,
        )

        response = self.client.get("/api/habits/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "чтение")

    def test_public_habits_visible_without_auth(self):
        user = User.objects.create_user(
            email="public@example.com",
            password="strongpass123",
            username="public",
        )
        Habit.objects.create(
            user=user,
            place="парк",
            time_moment=time(7, 0),
            action="пробежка",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="завтрак",
            duration=time(0, 2, 0),
            is_public=True,
        )

        self.client.credentials()  # убрать авторизацию
        response = self.client.get("/api/habits/public/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "пробежка")

    def test_cannot_access_foreign_habit_detail(self):
        other_user = User.objects.create_user(
            email="other2@example.com",
            password="strongpass123",
            username="other2",
        )
        foreign_habit = Habit.objects.create(
            user=other_user,
            place="офис",
            time_moment=time(11, 0),
            action="чай",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="печенье",
            duration=time(0, 2, 0),
            is_public=False,
        )

        response = self.client.get(f"/api/habits/{foreign_habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HabitValidatorsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="validator@example.com",
            password="strongpass123",
            username="validator",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def _base_valid_payload(self):
        return {
            "place": "дом",
            "time_moment": "08:00:00",
            "action": "делать зарядку",
            "is_pleasant": False,
            "linked_habit": None,
            "periodicity": "ежедневная",
            "reward": "кофе",
            "duration": "00:02:00",
            "is_public": False,
        }

    def test_reward_and_linked_habit_mutually_exclusive(self):
        pleasant = Habit.objects.create(
            user=self.user,
            place="дом",
            time_moment=time(6, 0),
            action="ванна",
            is_pleasant=True,
            periodicity="ежедневная",
            reward="",
            duration=time(0, 2, 0),
            is_public=False,
        )

        payload = self._base_valid_payload()
        payload["linked_habit"] = pleasant.id

        response = self.client.post("/api/habits/create/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reward", response.data)
        self.assertIn("linked_habit", response.data)

    def test_pleasant_habit_cannot_have_reward_or_linked(self):
        payload = self._base_valid_payload()
        payload["is_pleasant"] = True

        response = self.client.post("/api/habits/create/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_pleasant", response.data)

    def test_duration_cannot_exceed_120_seconds(self):
        payload = self._base_valid_payload()
        payload["duration"] = "00:02:01"

        response = self.client.post("/api/habits/create/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration", response.data)

    def test_linked_habit_must_be_pleasant(self):
        not_pleasant = Habit.objects.create(
            user=self.user,
            place="дом",
            time_moment=time(6, 0),
            action="уборка",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="кофе",
            duration=time(0, 2, 0),
            is_public=False,
        )

        payload = self._base_valid_payload()
        payload["reward"] = ""
        payload["linked_habit"] = not_pleasant.id

        response = self.client.post("/api/habits/create/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("linked_habit", response.data)

    def test_periodicity_not_less_frequent_than_seven_days(self):
        payload = self._base_valid_payload()
        payload["periodicity"] = "8"

        response = self.client.post("/api/habits/create/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("periodicity", response.data)


class HabitReminderTaskTests(APITestCase):
    def test_send_habit_reminders_sends_message_for_matching_time(self):
        user = User.objects.create_user(
            email="reminder@example.com",
            password="strongpass123",
            username="reminder",
            telegram_chat_id="999999",
        )

        now = timezone.now().time().replace(second=0, microsecond=0)

        Habit.objects.create(
            user=user,
            place="дом",
            time_moment=now,
            action="выпить воды",
            is_pleasant=False,
            periodicity="ежедневная",
            reward="",
            duration=time(0, 2, 0),
            is_public=False,
        )

        with patch("habits.tasks.send_telegram_message") as mock_send:
            send_habit_reminders()

        mock_send.assert_called_once()
