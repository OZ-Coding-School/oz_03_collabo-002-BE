from django import forms

from .models import ClassImages


class ClassImagesForm(forms.ModelForm):
    thumbnail_image = forms.ImageField(required=False)
    detail_image = forms.ImageField(required=False)
    description_image = forms.ImageField(required=False)

    class Meta:
        model = ClassImages
        fields = ["class_id", "thumbnail_image", "detail_image", "description_image"]
