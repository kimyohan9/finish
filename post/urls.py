# from django.urls import path
# from post.views import post_list, post_create, post_detail

# urlpatterns = [
#     path('', post_list, name='post_list'),
#     path('new/', post_create, name='post_create'),
#     path('<int:post_id>/', post_detail, name='post_detail'),
# ]


from django.urls import path
from .views import post_list, post_create, post_detail ,post_delete

urlpatterns = [
    path('list/', post_list, name='post_list'),  # 게시글 목록
    path('post/new/', post_create, name='post_create'),  # 게시글 작성
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/delete/', post_delete, name='post_delete'),
    ]
