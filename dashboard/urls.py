from django.urls import path

from .views import dashboard_index, dashboard_student

urlpatterns = [
    path("", dashboard_index, name="dashboard-index"),
    path("student/<str:student_id>/", dashboard_student, name="dashboard-student"),
]
