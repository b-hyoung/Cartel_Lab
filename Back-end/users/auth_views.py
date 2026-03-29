from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


def set_auth_cookies(response, access_token, refresh_token):
    jwt = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt['AUTH_COOKIE'],
        value=access_token,
        httponly=jwt['AUTH_COOKIE_HTTP_ONLY'],
        secure=jwt['AUTH_COOKIE_SECURE'],
        samesite=jwt['AUTH_COOKIE_SAMESITE'],
        max_age=int(jwt['ACCESS_TOKEN_LIFETIME'].total_seconds()),
    )
    response.set_cookie(
        key=jwt['AUTH_COOKIE_REFRESH'],
        value=refresh_token,
        httponly=jwt['AUTH_COOKIE_HTTP_ONLY'],
        secure=jwt['AUTH_COOKIE_SECURE'],
        samesite=jwt['AUTH_COOKIE_SAMESITE'],
        max_age=int(jwt['REFRESH_TOKEN_LIFETIME'].total_seconds()),
    )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        student_id = request.data.get('student_id', '').strip()
        password = request.data.get('password', '')

        user = authenticate(request, username=student_id, password=password)
        if not user:
            return Response({'error': '학번 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        response = Response({
            'name': user.name,
            'is_staff': user.is_staff,
            'class_group': user.class_group,
        })
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        jwt = settings.SIMPLE_JWT
        response = Response({'detail': '로그아웃되었습니다.'})
        response.delete_cookie(jwt['AUTH_COOKIE'])
        response.delete_cookie(jwt['AUTH_COOKIE_REFRESH'])
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        jwt = settings.SIMPLE_JWT
        refresh_token = request.COOKIES.get(jwt['AUTH_COOKIE_REFRESH'])
        if not refresh_token:
            return Response({'error': '리프레시 토큰이 없습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            response = Response({'detail': '토큰이 갱신되었습니다.'})
            set_auth_cookies(response, str(refresh.access_token), str(refresh))
            return response
        except Exception:
            return Response({'error': '유효하지 않은 토큰입니다.'}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'name': user.name,
            'student_id': user.student_id,
            'is_staff': user.is_staff,
            'class_group': user.class_group,
            'grade': user.grade,
            'profile_image': request.build_absolute_uri(user.profile_image.url) if user.profile_image else None,
        })
