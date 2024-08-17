from django.db import models


class Class(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.IntegerField(blank=False, default=0)
    require_person = models.IntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    address = models.TextField(blank=False, default="")

    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ClassDate(models.Model):
    course = models.ForeignKey(Class, related_name="dates", on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)


class ClassImages(models.Model):
    course = models.ForeignKey(Class, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    def __str__(self):
        return f"{self.course.title}"
