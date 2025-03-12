from django.urls import path
from .views import fetch_and_store

urlpatterns = [
    path("", fetch_and_store, name="crawl"),
]
