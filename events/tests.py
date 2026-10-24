
from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Reservation


class EventHubAPITests(APITestCase):

    def setUp(self):
        self.event = Event.objects.create(
            title="Django Conference",
            venue="Agra Convention Centre",
            date=date.today() + timedelta(days=30),
            total_seats=5,
            available_seats=5,
            status="upcoming",
        )

        self.events_url = "/api/events/"
        self.reservations_url = "/api/reservations/"

        self.valid_reservation = {
            "event": self.event.id,
            "attendee_name": "Asha Sharma",
            "attendee_email": "asha@example.com",
            "seats_reserved": 2,
        }

    def test_list_events(self):
        response = self.client.get(self.events_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_events_by_status(self):
        response = self.client.get(
            self.events_url, {"status": "upcoming"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_events_by_venue(self):
        response = self.client.get(
            self.events_url, {"venue": "agra"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_reservation_deducts_seats(self):
        response = self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(response.data["status"], "confirmed")

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 3)

    def test_overbooking_is_rejected(self):
        payload = {
            **self.valid_reservation,
            "seats_reserved": 6,
        }

        response = self.client.post(
            self.reservations_url, payload, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_zero_seats_are_rejected(self):
        payload = {
            **self.valid_reservation,
            "seats_reserved": 0,
        }

        response = self.client.post(
            self.reservations_url, payload, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_completed_event_rejects_reservation(self):
        self.event.status = "completed"
        self.event.save()

        response = self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_cancel_reservation_restores_seats(self):
        created = self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        self.assertEqual(
            created.status_code, status.HTTP_201_CREATED
        )

        reservation_id = created.data["id"]
        cancel_url = (
            f"{self.reservations_url}{reservation_id}/cancel/"
        )

        response = self.client.post(cancel_url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(response.data["status"], "cancelled")

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_cannot_cancel_twice(self):
        created = self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        cancel_url = (
            f"{self.reservations_url}{created.data['id']}/cancel/"
        )

        self.client.post(cancel_url)
        response = self.client.post(cancel_url)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_filter_reservations_by_event_id(self):
        self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        response = self.client.get(
            self.reservations_url,
            {"event_id": self.event.id},
        )

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(len(response.data), 1)

    def test_reservations_count_includes_confirmed_only(self):
        reservation = self.client.post(
            self.reservations_url,
            self.valid_reservation,
            format="json",
        )

        self.assertEqual(
            reservation.status_code, status.HTTP_201_CREATED
        )

        response = self.client.get(self.events_url)

        self.assertEqual(
            response.data[0]["reservations_count"], 1
        )

    def test_zero_total_seats_are_rejected(self):
        payload = {
            "title": "Invalid Event",
            "venue": "Agra",
            "date": (date.today() + timedelta(days=30)).isoformat(),
            "total_seats": 0,
            "available_seats": 0,
            "status": "upcoming",
        }

        response = self.client.post(
            self.events_url, payload, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_negative_available_seats_are_rejected(self):
        payload = {
            "title": "Invalid Event",
            "venue": "Agra",
            "date": (date.today() + timedelta(days=30)).isoformat(),
            "total_seats": 5,
            "available_seats": -1,
            "status": "upcoming",
        }

        response = self.client.post(
            self.events_url, payload, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_available_seats_cannot_exceed_total_seats(self):
        payload = {
            "title": "Invalid Event",
            "venue": "Agra",
            "date": (date.today() + timedelta(days=30)).isoformat(),
            "total_seats": 5,
            "available_seats": 6,
            "status": "upcoming",
        }

        response = self.client.post(
            self.events_url, payload, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )
