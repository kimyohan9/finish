from django.contrib.auth import authenticate ,logout,login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from .serializers import UserRegisterSerializer
from django.shortcuts import render
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import requests


KAKAO_CLIENT_ID = "a6971a25bb35dc1113d81b5713a3ccc7"  # ✅ 여기에 본인의 카카오 REST API 키 입력
KAKAO_REDIRECT_URI = "http://127.0.0.1:8000/accounts/kakao/login/callback/"  # ✅ 카카오 로그인 리디렉트 URL

User = get_user_model()

@api_view(['POST'])
# def kakao_login(request):
#     """
#     프론트엔드에서 카카오 OAuth2 인증 후 access_token을 전달받아 로그인 처리하는 API
#     """
#     kakao_code = request.data.get("code")
#     if not kakao_code:
#         return Response({"error": "인증 코드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

#     # 카카오 액세스 토큰 요청
#     kakao_token_url = "https://kauth.kakao.com/oauth/token"
#     data = {
#         'grant_type': 'authorization_code',
#         'client_id': 'a6971a25bb35dc1113d81b5713a3ccc7',
#         'redirect_uri': 'http://127.0.0.1:8000/accounts/kakao/callback/',
#         'code': kakao_code
#     }

#     response = requests.post(kakao_token_url, data=data)

#     if response.status_code != 200:
#         return Response({"error": "카카오에서 액세스 토큰을 가져오는 데 실패했습니다."}, status=response.status_code)

#     # 액세스 토큰을 얻은 후 카카오 사용자 정보 요청
#     kakao_data = response.json()
#     kakao_access_token = kakao_data.get("access_token")
#     if not kakao_access_token:
#         return Response({"error": "액세스 토큰을 받는 데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

#     kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
#     headers = {"Authorization": f"Bearer {kakao_access_token}"}
#     user_info_response = requests.get(kakao_user_info_url, headers=headers)

#     if user_info_response.status_code != 200:
#         return Response({"error": "카카오 사용자 정보를 가져오는 데 실패했습니다."}, status=user_info_response.status_code)

#     kakao_user_data = user_info_response.json()
#     kakao_id = kakao_user_data.get("id")
#     # kakao_email = kakao_user_data.get("kakao_account", {}).get("email")

#     # if not kakao_email:
#     #     return Response({"error": "이메일 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

#     # 사용자 조회 또는 생성
#     user, created = User.objects.get_or_create(
#         username=f"kakao_{kakao_id}",
#         # defaults={"email": kakao_email}
#     )

#     # 로그인 처리 및 토큰 발급
#     token, _ = Token.objects.get_or_create(user=user)

#     return Response({
#         "message": "카카오 로그인 성공!",
#         "user_id": user.id,
#         "token": token.key
#     }, status=status.HTTP_200_OK)
def kakao_login(request):
    """
    프론트엔드에서 카카오 OAuth2 인증 후 access_token을 전달받아 로그인 처리하는 API
    """
    kakao_code = request.data.get("code")
    if not kakao_code:
        return Response({"error": "인증 코드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 카카오 액세스 토큰 요청
    kakao_token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': '',
        'redirect_uri': 'http://127.0.0.1:8000/accounts/kakao/callback/',
        'code': kakao_code  # 받은 인증 코드
    }
    kakao_access_token = request.data.get("access_token")

    if not kakao_access_token:
        return Response({"error": "Access Token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {kakao_access_token}"}
    response = requests.get(kakao_user_info_url, headers=headers)
    if response.status_code != 200:
         return Response({"error": "실패", "details": response.json()}, status=response.status_code)

    # if response.status_code != 200:
    #     return Response({"error": "카카오 사용자 정보를 가져오는 데 실패했습니다."}, status=response.status_code)

    kakao_data = response.json()
    kakao_id = kakao_data.get("id")
    kakao_email = kakao_data.get("kakao_account", {}).get("email")

    if not kakao_email:
        return Response({"error": "이메일 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(username=f"kakao_{kakao_id}", defaults={"email": kakao_email})

    # 로그인 처리 및 토큰 발급
    token, _ = Token.objects.get_or_create(user=user)
    #로그인 함수 그래야지 로그인세션 유지
    return Response({
        "message": "카카오 로그인 성공!",
        "user_id": user.id,
        "token": token.key
    }, status=status.HTTP_200_OK)

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
        login(request, user)
        return Response({"message": "로그인 성공!", "token": token.key}, status=status.HTTP_200_OK)
    
    return Response({"error": "로그인 실패! 올바른 자격 증명을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_api(request):
    user = request.user
    Token.objects.filter(user=user).delete()
    logout(request)
    return Response({"message": "로그아웃 성공!"}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    """
    사용자의 프로필 페이지를 조회하는 API 뷰
    """
    def get(self, request):
        profile = request.user.profile  # 현재 로그인한 사용자의 프로필
        serializer = ProfileSerializer(profile)  # 프로필 직렬화
        return Response(serializer.data)

class EditProfileView(APIView):
    """
    사용자가 자신의 프로필을 수정하는 API 뷰
    """
    parser_classes = (MultiPartParser, FormParser)  # 파일 업로드 처리

    def get(self, request):
        profile = request.user.profile  # 현재 로그인한 사용자의 프로필
        serializer = ProfileSerializer(profile)  # 프로필 직렬화
        return Response(serializer.data)  # GET 요청 시 현재 프로필 데이터 반환

    def post(self, request):
        profile = request.user.profile  # 현재 로그인한 사용자의 프로필
        serializer = ProfileSerializer(profile, data=request.data, partial=True)  # 수정된 데이터로 직렬화
        if serializer.is_valid():
            serializer.save()  # 유효한 데이터는 저장
            return Response({'message': '프로필이 수정되었습니다!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
