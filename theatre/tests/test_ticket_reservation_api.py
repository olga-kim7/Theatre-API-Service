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
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=None)

    def test_unauthorized_ticket_list(self):
        response = self.client.get(TICKET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_ticket_detail(self):
        response = self.client.get(get_ticket_retrieve_url(1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthorizedTestCase(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            password="PASSWORD",
            email="mail@test.com"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.user2 = get_user_model().objects.create_user(
            password="PASSWORD",
            email="mail2@test.com"
        )
        self.reservation1 = sample_reservation(user=self.user1)
        self.reservation2 = sample_reservation(user=self.user2)
        self.theatre_hall = sample_theatre_hall()
        self.play = sample_play()
        self.performance = sample_performance(play=self.play, theatre_hall=self.theatre_hall)
        self.ticket1 = sample_ticket(row=1, seat=1, performance=self.performance, reservation=self.reservation1)
        self.ticket2 = sample_ticket(row=2, seat=2, performance=self.performance, reservation=self.reservation2)
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
            "performance": self.performance,
        }
        response = self.client.post(TICKET_LIST_URL, ticket)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

    # def test_ticket_update(self):
    #     # First, create a ticket
    #     create_ticket_data = {
    #         "row": 1,
    #         "seat": 13,
    #         "performance": self.performance.id,
    #         "reservation": self.reservation1.id,
    #     }
    #     response = self.client.post(TICKET_LIST_URL, create_ticket_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     # Retrieve the created ticket's ID
    #     ticket_id = response.data['id']
    #     update_ticket_url = get_ticket_retrieve_url(ticket_id)
    #
    #     # Define updated ticket data
    #     updated_ticket_data = {
    #         "row": 12,
    #         "seat": 7,
    #         # Optionally include performance and reservation if your API requires them
    #         "performance": self.performance.id,
    #         "reservation": self.reservation1.id,
    #     }
    #
    #     # Perform the update
    #     response = self.client.put(update_ticket_url, updated_ticket_data, format='json')
    #
    #     # Check if the update was successful
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)  # Assuming successful update returns 200 OK
    #
    # def test_ticket_delete(self):
    #     ticket = sample_ticket(
    #         row=1,
    #         seat=3,
    #         performance=self.performance,
    #         reservation=self.reservation1
    #     )
    #     response = self.client.delete(get_ticket_retrieve_url(ticket.id))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #
