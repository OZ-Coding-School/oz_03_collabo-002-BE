from django import forms

from .models import ClassImages


class ClassImagesForm(forms.ModelForm):
    image = forms.ImageField()  # 파일 업로드 필드 추가

    class Meta:
        model = ClassImages
        fields = ["class_id", "image"]  # image_url은 업로드 후 URL 저장
