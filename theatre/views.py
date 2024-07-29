from django.db.models import Count, F
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from theatre.models import (
    Genre,
    Actor,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket
)
from theatre.serializers import (
    GenreSerializer,
    ActorSerializer,
    PlaySerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer, PlayListSerializer, PlayDetailSerializer, PerformanceListSerializer, PerformanceDetailSerializer,
    ReservationListSerializer, ReservationCreateSerializer
)

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        actors = self.request.query_params.get("actors")
        genres = self.request.query_params.get("genres")
        title = self.request.query_params.get("title")
        if actors:
            actors_ids = [int(str_id) for str_id in actors.split(",")]
            queryset = queryset.filter(actors__in=actors_ids)
        if genres:
            genres_ids = [int(str_id) for str_id in genres.split(",")]
            queryset = queryset.filter(genres__in=genres_ids)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all().select_related("play")
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")
        play = self.request.query_params.get("play")
        if date:
            queryset = queryset.filter(show_time__date=date)
        if play:
            queryset = queryset.filter(play__id=play)
        if self.action == "list":
            queryset = (
                queryset
                .select_related("theatre_hall", "play")
                .annotate(
                    holded=Count("tickets"),
                    total=F(
                        "theatre_hall__row") * F("theatre_hall__seats_in_row"
                                                 ),
                    tickets_available=F("total") - F("holded"),
                )

            )
        return queryset


class ReservationPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().select_related("user")
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer

    def get_queryset(self):
        if self.action == "list":
            return Reservation.objects.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
