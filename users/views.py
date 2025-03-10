from django.contrib.auth import authenticate ,logout,login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from .serializers import UserRegisterSerializer
from django.shortcuts import render
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer


# KAKAO_CLIENT_ID = "a6971a25bb35dc1113d81b5713a3ccc7"  # ✅ 여기에 본인의 카카오 REST API 키 입력
# KAKAO_REDIRECT_URI = "http://127.0.0.1:8000/accounts/kakao/login/callback/"  # ✅ 카카오 로그인 리디렉트 URL

# User = get_user_model()

# @api_view(['POST'])
# def kakao_login(request):
#     """
#     프론트엔드에서 카카오 OAuth2 인증 후 access_token을 전달받아 로그인 처리하는 API
#     """
#     kakao_access_token = request.data.get("access_token")

#     if not kakao_access_token:
#         return Response({"error": "Access Token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

#     kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
#     headers = {"Authorization": f"Bearer {kakao_access_token}"}
#     response = requests.get(kakao_user_info_url, headers=headers)

#     if response.status_code != 200:
#         return Response({"error": "카카오 사용자 정보를 가져오는 데 실패했습니다."}, status=response.status_code)

#     kakao_data = response.json()
#     kakao_id = kakao_data.get("id")
#     kakao_email = kakao_data.get("kakao_account", {}).get("email")

#     if not kakao_email:
#         return Response({"error": "이메일 정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

#     user, created = User.objects.get_or_create(username=f"kakao_{kakao_id}", defaults={"email": kakao_email})

#     # 로그인 처리 및 토큰 발급
#     token, _ = Token.objects.get_or_create(user=user)

#     return Response({
#         "message": "카카오 로그인 성공!",
#         "user_id": user.id,
#         "token": token.key
#     }, status=status.HTTP_200_OK)

@api_view(['POST'])
def register_api(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "회원가입 성공!", "user_id": user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @renderer_classes([TemplateHTMLRenderer, JSONRenderer])
def login_api(request):
    # if request.method == 'GET':
        # return Response(template_name='registration/login.html')

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