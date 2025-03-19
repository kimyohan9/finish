from django.urls import path
from .views import soil_recommendation_view

urlpatterns = [
    path('', soil_recommendation_view, name='soil_recommendation'), 
]
