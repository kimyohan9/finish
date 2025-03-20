from django.contrib.auth import authenticate ,logout,login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserRegisterSerializer, UserSerializer, ProfileSerializer
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
import requests
from rest_framework.permissions import IsAuthenticated 
from django.views.decorators.csrf import csrf_exempt #일시적 로그인 오류해결 배포시 같이 삭제하기
from users.models import Profile  # Profile 모델 임포트


KAKAO_CLIENT_ID = "a6971a25bb35dc1113d81b5713a3ccc7"  # ✅ 여기에 본인의 카카오 REST API 키 입력
KAKAO_REDIRECT_URI = "http://127.0.0.1:8000/accounts/kakao/login/callback/"  # ✅ 카카오 로그인 리디렉트 URL

User = get_user_model()

@api_view(['POST'])

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

@csrf_exempt # 포스트맨 테스트 csrf 토큰에러 일시 제거 베포시 삭제
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
        try:
            # 사용자의 프로필을 가져옵니다
            profile = request.user.profile
        except Profile.DoesNotExist:
            # 프로필이 존재하지 않으면 예외 처리
            return Response({"message": "프로필이 없습니다. 프로필을 만드세요!"}, status=status.HTTP_404_NOT_FOUND)
        
        # 프로필이 존재하면 직렬화하여 반환
        serializer = ProfileSerializer(profile)
        return Response(serializer.data) 
    
        
# class EditProfileView(APIView):
#     """
#     사용자가 자신의 프로필을 수정하는 API 뷰
#     """
#     parser_classes = (MultiPartParser, FormParser)  # 파일 업로드 처리

#     def get(self, request):
#         profile = request.user.profile  # 현재 로그인한 사용자의 프로필
#         serializer = ProfileSerializer(profile)  # 프로필 직렬화
#         return Response(serializer.data)  # GET 요청 시 현재 프로필 데이터 반환

#     def post(self, request):
#         profile = request.user.profile  # 현재 로그인한 사용자의 프로필
#         serializer = ProfileSerializer(profile, data=request.data, partial=True)  # 수정된 데이터로 직렬화
#         if serializer.is_valid():
#             serializer.save()  # 유효한 데이터는 저장
#             return Response({'message': '프로필이 수정되었습니다!'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원 정보 수정 (이름, 이메일 등)
class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)  # 부분 업데이트 가능
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원 탈퇴 (DB 기록은 유지, 비활성화)
class UserDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False  # 계정을 비활성화 (DB 기록 유지)
        user.save()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)

