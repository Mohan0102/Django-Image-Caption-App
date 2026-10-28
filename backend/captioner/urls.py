from django.urls import path
from .views import CaptionView, HealthView

urlpatterns = [
    path("caption/", CaptionView.as_view()),
    path("health/", HealthView.as_view()),
]
