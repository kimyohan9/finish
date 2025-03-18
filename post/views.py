from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

User = get_user_model()

# 게시글 목록 및 생성
class PostListAPIView(APIView):
    # permission_classes = [IsAuthenticated] #유저기능 완료후 권한 넣고 test

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 게시글 상세 조회 및 댓글 작성
class PostDetailAPIView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        """관리자만 댓글 작성 가능"""
        if not request.user.is_staff:
            return Response({"error": "관리자만 댓글을 작성할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 게시글 삭제
class PostDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user == post.author or request.user.is_staff:
            post.delete()
            return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
