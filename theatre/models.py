from django.contrib.auth.models import User
from django.db import models


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    plays = models.ManyToManyField(Play, related_name="actors")


class Genre(models.Model):
    name = models.CharField(max_length=255)
    plays = models.ManyToManyField(Play, related_name="genres")


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    row = models.IntegerField()
    seats_in_row = models.IntegerField()


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="performances")
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE, related_name="performances")
    show_time = models.DateTimeField()


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")
