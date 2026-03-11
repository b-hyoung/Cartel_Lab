from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["student_id", "name", "password1", "password2"]
        labels = {
            "student_id": "학번",
            "name": "이름",
            "password1": "비밀번호",
            "password2": "비밀번호 확인",
        }


class LoginForm(forms.Form):
    student_id = forms.CharField(label="학번", max_length=20)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "학번 또는 비밀번호가 올바르지 않습니다.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        student_id = cleaned_data.get("student_id")
        password = cleaned_data.get("password")

        if student_id and password:
            self.user_cache = authenticate(
                self.request,
                student_id=student_id,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileUpdateForm(forms.ModelForm):
    resume_file = forms.FileField(label="이력서 파일", required=False)

    class Meta:
        model = User
        fields = ["github_url", "resume_file"]
        labels = {
            "github_url": "GitHub 링크",
            "resume_file": "이력서 파일",
        }

    def clean_github_url(self):
        value = (self.cleaned_data.get("github_url") or "").strip()
        if value and "github.com" not in value:
            raise forms.ValidationError("GitHub 프로필 링크를 입력해 주세요.")
        return value

    def clean_resume_file(self):
        uploaded = self.cleaned_data.get("resume_file")
        if not uploaded:
            return uploaded

        name = uploaded.name.lower()
        if not (name.endswith(".pdf") or name.endswith(".txt")):
            raise forms.ValidationError("이력서는 PDF 또는 TXT 파일만 업로드할 수 있습니다.")
        return uploaded
