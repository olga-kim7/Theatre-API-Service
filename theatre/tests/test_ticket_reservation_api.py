from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from theatre.models import Ticket, TheatreHall, Reservation, Play, Genre, Performance
from theatre.serializers import TicketSerializer

TICKET_LIST_URL = reverse("theatre:ticket-list")


def get_ticket_retrieve_url(ticket_id):
    return reverse("theatre:ticket-detail", args=[ticket_id])


def sample_reservation(user, **params):
    default = {
        "created_at": timezone.now(),
    }
    default.update(params)
    return Reservation.objects.create(user=user, **default)


def sample_performance(play, theatre_hall, **params):
    default = {
        "show_time": timezone.now(),
    }
    default.update(params)
    return Performance.objects.create(play=play, theatre_hall=theatre_hall, **default)


def sample_genre(**params):
    default = {"name": "test genre"}
    default.update(params)
    return Genre.objects.create(**default)


def sample_play(**params):
    default = {
        "title": "test title",
        "description": "test description",
    }
    default.update(params)
    return Play.objects.create(**default)


def sample_theatre_hall(**params):
    default = {
        "name": "test theatre_hall",
        "row": 5,
        "seats_in_row": 10,
    }
    default.update(params)
    return TheatreHall.objects.create(**default)


def sample_ticket(performance, reservation, **params):
    default = {
        "row": 1,
        "seat": 1,
        "performance": performance,
        "reservation": reservation,
    }
    default.update(params)
    return Ticket.objects.create(**default)


class UnAuthorizedTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.client.force_authenticate(user=None)

    def test_unauthorized_ticket_list(self):
        response = self.client.get(TICKET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_ticket_detail(self):
        response = self.client.get(get_ticket_retrieve_url(1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            password="PASSWORD",
            email="mail@test.com"
        )
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.user1)

        cls.reservation1 = sample_reservation(user=cls.user1)
        cls.theatre_hall = sample_theatre_hall()
        cls.play = sample_play()
        cls.performance = sample_performance(play=cls.play, theatre_hall=cls.theatre_hall)
        cls.ticket1 = sample_ticket(row=1, seat=1, performance=cls.performance, reservation=cls.reservation1)

    def test_ticket_list(self):
        serializer1 = TicketSerializer(self.ticket1)
        serializer2 = TicketSerializer(self.ticket2)
        response = self.client.get(TICKET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_ticket_detail(self):
        serializer = TicketSerializer(self.ticket1)
        response = self.client.get(get_ticket_retrieve_url(self.ticket1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_ticket_create(self):
        ticket = {
            "row": 3,
            "seat": 3,
            "reservation": self.reservation1.id,
            "performance": self.performance.id,
        }
        response = self.client.post(TICKET_LIST_URL, ticket, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_update(self):
        create_ticket_data = {
            "row": 1,
            "seat": 13,
            "performance": self.performance.id,
            "reservation": self.reservation1.id,
        }
        response = self.client.post(TICKET_LIST_URL, create_ticket_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ticket_id = response.data['id']
        update_ticket_url = get_ticket_retrieve_url(ticket_id)

        updated_ticket_data = {
            "row": 12,
            "seat": 7,
            "performance": self.performance.id,
            "reservation": self.reservation1.id,
        }

        response = self.client.put(update_ticket_url, updated_ticket_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_delete(self):
        ticket = sample_ticket(
            row=1,
            seat=3,
            performance=self.performance,
            reservation=self.reservation1
        )
        response = self.client.delete(get_ticket_retrieve_url(ticket.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
