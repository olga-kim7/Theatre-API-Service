from django.test import TestCase
from django.utils import timezone
from theatre.models import Play, TheatreHall, Performance, Actor, Genre
from theatre.tests.test_ticket_reservation_api import sample_performance

class PerformanceModelTests(TestCase):

    def test_sample_performance_creates_object(self):
        # Створюємо об'єкти Genre та Actor для тестування
        genre1 = Genre.objects.create(name="Drama")
        genre2 = Genre.objects.create(name="Comedy")
        actor1 = Actor.objects.create(first_name="John", last_name="Doe")
        actor2 = Actor.objects.create(first_name="Jane", last_name="Smith")

        # Створюємо об'єкт Play з жанрами та акторами
        play = Play.objects.create(
            title="Test Play",
            description="A test play description",
            image=None
        )
        play.genres.add(genre1, genre2)
        play.actors.add(actor1, actor2)

        # Створюємо об'єкт TheatreHall для тестування
        theatre_hall = TheatreHall.objects.create(name="Main Hall", row=2, seats_in_row=7)

        # Викликаємо sample_performance для створення Performance
        performance = sample_performance(play=play, theatre_hall=theatre_hall)

        # Перевіряємо, чи Performance зберігся в базі даних
        self.assertEqual(Performance.objects.count(), 1)

        # Перевіряємо, що створений об'єкт має правильні значення
        self.assertEqual(performance.play, play)
        self.assertEqual(performance.theatre_hall, theatre_hall)
        self.assertAlmostEqual(performance.show_time, timezone.now(), delta=timezone.timedelta(seconds=1))

        # Додатково перевіряємо поля Play
        self.assertEqual(play.title, "Test Play")
        self.assertEqual(play.description, "A test play description")
        self.assertIn(genre1, play.genres.all())
        self.assertIn(genre2, play.genres.all())
        self.assertIn(actor1, play.actors.all())
        self.assertIn(actor2, play.actors.all())
