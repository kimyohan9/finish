from django.contrib.auth import authenticate ,logout, login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserRegisterSerializer


@api_view(['POST'])
def register_api(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "회원가입 성공!", "user_id": user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "로그인 성공!", "token": token.key}, status=status.HTTP_200_OK)
    
    return Response({"error": "로그인 실패! 올바른 자격 증명을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_api(request):
    user = request.user
    Token.objects.filter(user=user).delete()
    logout(request)
    return Response({"message": "로그아웃 성공!"}, status=status.HTTP_200_OK)