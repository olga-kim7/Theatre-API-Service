from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    PlayViewSet,
    GenreViewSet,
    ActorViewSet,
    TheatreHallViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)

app_name = "theatre"

router = routers.DefaultRouter()

router.register("plays", PlayViewSet)
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
