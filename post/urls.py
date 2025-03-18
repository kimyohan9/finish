

from django.urls import path
from .views import (
    PostListAPIView, PostDetailAPIView, PostDeleteAPIView,
    
)

urlpatterns = [
    path('', PostListAPIView.as_view(), name='post_list'),
    path('<int:post_id>/', PostDetailAPIView.as_view(), name='post_detail'),
    path('<int:post_id>/delete/', PostDeleteAPIView.as_view(), name='post_delete'),
]
