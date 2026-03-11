import math
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import AttendanceRecord, LocationSetting


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    두 좌표 사이의 직선 거리를 계산 (미터 단위)
    """
    R = 6371000  # 지구 반지름 (미터)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@login_required
def index(request):
    """
    출결 메인 페이지
    """
    return render(request, "attendance/index.html")


def attendance_list(request):
    """
    HTMX 폴링을 위한 실시간 출결 목록 (부분 템플릿)
    """
    today = timezone.localdate()
    records = AttendanceRecord.objects.filter(attendance_date=today).order_by("-check_in_at")
    return render(request, "attendance/partial_list.html", {"records": records})


@login_required
@require_POST
def check_in(request):
    """
    사용자 위치를 기반으로 출석 처리
    """
    try:
        import json
        data = json.loads(request.body)
        user_lat = float(data.get("latitude"))
        user_lon = float(data.get("longitude"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "잘못된 위치 정보입니다."}, status=400)

    # 활성화된 출결 가능 위치 정보를 가져옴
    location = LocationSetting.objects.filter(is_active=True).first()
    if not location:
        return JsonResponse({"status": "error", "message": "설정된 출결 위치가 없습니다. 관리자에게 문의하세요."}, status=400)

    distance = haversine_distance(user_lat, user_lon, location.latitude, location.longitude)

    if distance > location.radius:
        return JsonResponse({
            "status": "error", 
            "message": f"위치 범위를 벗어났습니다. (현재 약 {int(distance)}m 거리)"
        }, status=403)

    # 오늘 이미 출석했는지 확인
    today = timezone.localdate()
    record, created = AttendanceRecord.objects.get_or_create(
        user=request.user,
        attendance_date=today,
        defaults={"status": "present"}
    )

    if not created:
        return JsonResponse({"status": "info", "message": "이미 오늘 출석 완료되었습니다."})

    return JsonResponse({"status": "success", "message": f"{location.name}에 출석 완료되었습니다!"})


@login_required
@require_POST
def check_out(request):
    """
    사용자 위치를 기반으로 퇴실 처리
    """
    try:
        import json
        data = json.loads(request.body)
        user_lat = float(data.get("latitude"))
        user_lon = float(data.get("longitude"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "잘못된 위치 정보입니다."}, status=400)

    location = LocationSetting.objects.filter(is_active=True).first()
    if not location:
        return JsonResponse({"status": "error", "message": "설정된 위치 정보가 없습니다."}, status=400)

    distance = haversine_distance(user_lat, user_lon, location.latitude, location.longitude)

    if distance > location.radius:
        return JsonResponse({
            "status": "error", 
            "message": f"위치 범위를 벗어났습니다. (현재 약 {int(distance)}m 거리)"
        }, status=403)

    # 오늘 출석 기록 찾기
    today = timezone.localdate()
    try:
        record = AttendanceRecord.objects.get(user=request.user, attendance_date=today)
        if record.check_out_at:
            return JsonResponse({"status": "info", "message": "이미 퇴실 처리가 완료되었습니다."})
        
        record.check_out_at = timezone.now()
        record.save()
        return JsonResponse({"status": "success", "message": "퇴실 처리가 완료되었습니다. 수고하셨습니다!"})
    except AttendanceRecord.DoesNotExist:
        return JsonResponse({"status": "error", "message": "오늘 출석 기록이 없습니다. 먼저 출석체크를 해주세요."}, status=400)


@login_required
@require_POST
def set_location(request):
    """
    관리자가 현재 자신의 위치를 출결 허용 위치로 설정함
    """
    if not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "권한이 없습니다."}, status=403)

    try:
        import json
        data = json.loads(request.body)
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        name = data.get("name", "연구실")
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "잘못된 위치 정보입니다."}, status=400)

    # 기존 활성 위치를 업데이트하거나 새로 생성
    location, created = LocationSetting.objects.update_or_create(
        is_active=True,
        defaults={
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "radius": 50.0  # 기본 반경 50m
        }
    )

    return JsonResponse({
        "status": "success", 
        "message": f"현재 위치({lat}, {lon})가 '{name}'(으)로 설정되었습니다."
    })
