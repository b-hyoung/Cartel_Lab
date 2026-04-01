from django.urls import path

from .views import (
    QuizAdminApiView,
    QuizCreateApiView,
    QuizDeleteApiView,
    QuizEditApiView,
    QuizPageApiView,
    QuizSubmitApiView,
)

urlpatterns = [
    path("", QuizPageApiView.as_view(), name="quiz-api-index"),
    path("admin/", QuizAdminApiView.as_view(), name="quiz-api-admin"),
    path("create/", QuizCreateApiView.as_view(), name="quiz-api-create"),
    path("<int:quiz_id>/edit/", QuizEditApiView.as_view(), name="quiz-api-edit"),
    path("<int:quiz_id>/delete/", QuizDeleteApiView.as_view(), name="quiz-api-delete"),
    path("<int:quiz_id>/submit/", QuizSubmitApiView.as_view(), name="quiz-api-submit"),
]
