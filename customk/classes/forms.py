from django import forms

from .models import ClassImages


class ClassImagesForm(forms.ModelForm):
    images = forms.ImageField()

    class Meta:
        model = ClassImages
        fields = ["class_id", "images"]
