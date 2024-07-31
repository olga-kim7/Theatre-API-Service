from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayListSerializer, PlayDetailSerializer


PLAY_URL = reverse("theatre:play-list")


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


def sample_play(**params):
    defaults = {
        "title": "Test Play",
        "description": "Test Play Description",
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


def sample_actor(**params):
    defaults = {
        "first_name": "Fname",
        "last_name": "Lname",
    }
    defaults.update(params)
    return Actor.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Test Genre",
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


class UnauthenticatedPlayApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_play_list(self):
        play = sample_play()
        actor = sample_actor(first_name="Lili", last_name="Down")
        genre = sample_genre(name="Drama")
        play.actors.add(actor)
        play.genres.add(genre)
        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_play_by_title(self):
        play = sample_play()
        play1 = sample_play(
            title="Play2",
            description="Play Description",
        )
        response = self.client.get(PLAY_URL, {f"title": play.title})
        serializer_play = PlayListSerializer(play)
        serializer_play1 = PlayListSerializer(play1)
        self.assertIn(serializer_play.data, response.data)
        self.assertNotIn(serializer_play1.data, response.data)


    def test_filter_play_by_genre(self):
        play = sample_play(
            title="Play",
        )
        play1 = sample_play(
            title="Play1",
        )
        genre = sample_genre(name="Drama")
        play.genres.add(genre)
        serializer_with_genre = PlayListSerializer(play)
        serializer_without_genre = PlayListSerializer(play1)
        response = self.client.get(PLAY_URL, {f"genres": genre.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_with_genre.data, response.data)
        self.assertNotIn(serializer_without_genre.data, response.data)

    def test_filter_play_by_actor(self):
        play = sample_play()
        play1 = sample_play()
        actor = sample_actor(first_name="Olia", last_name="Kim")
        play.actors.add(actor)
        serializer_with_actor = PlayListSerializer(play)
        serializer_without_actor = PlayListSerializer(play1)
        response = self.client.get(PLAY_URL, {f"actors": actor.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_with_actor.data, response.data)
        self.assertNotIn(serializer_without_actor.data, response.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.actors.add(sample_actor(first_name="Olia", last_name="Kim"))
        url = detail_url(play.id)
        response = self.client.get(url)
        serializer = PlayDetailSerializer(play)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "Test Play",
            "description": "Test Play Description"
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="testpassword123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.actor = sample_actor(first_name="Lili", last_name="Down")
        self.genre = sample_genre(name="Drama")

    def test_create_play(self):
        payload = {
            "title": "Test play",
            "description": "Test play Description",
            "genres": [self.genre.id],
            "actors": [self.actor.id],
        }
        response = self.client.post(PLAY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(pk=response.data["id"])

        self.assertEqual(play.title, payload["title"])
        self.assertEqual(play.description, payload["description"])

        self.assertIn(self.genre, play.genres.all())
        self.assertIn(self.actor, play.actors.all())

    def test_create_play_genre(self):
        payload = {
            "title": "Test Play",
            "description": "Test Play Description",
            "genres": [self.genre.id],
            "actors": [self.actor.id],
        }

        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(pk=res.data["id"])
        genres = play.genres.all()
        self.assertEqual(genres.count(), 1)
        self.assertIn(self.genre, genres)

    def test_delete_play_not_allowed(self):
        play = sample_play()
        url = detail_url(play.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
