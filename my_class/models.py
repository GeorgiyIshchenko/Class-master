from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from PIL import Image


def generate_teacher_filename(instance,filename):
        filename = instance.author.first_name+instance.author.last_name+"_на_"+str(instance.date)+filename
        print(filename)
        return "teachers_media/{0}/{1}".format(instance.author.username,filename)


def generate_student_filename(instance,filename):
        filename = instance.author.username+"_на_"+str(instance.article.date)+filename
        return "students_media/{0}/{1}".format(instance.author.username,filename)


class Task(models.Model):
    title=models.CharField(max_length=32)
    body=RichTextUploadingField(blank=True,null=True)
    date=models.DateField()
    current_class = models.ForeignKey('Class', on_delete=models.CASCADE, null=True, blank=True)
    author=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True,
        null=True)
    published_date=models.DateTimeField(auto_now_add=True)
    max_mark = models.IntegerField(default=5)

    def __str__(self): 
        return self.title+" | "+str(self.pk)


    def get_absolute_url(self): 
        return reverse('taskcontent_url',kwargs={'pk':self.pk})


    class Meta:
        verbose_name = "Задания"
        verbose_name_plural = "Задания"

class Files(models.Model):

    file = models.FileField(upload_to=generate_teacher_filename, blank=True, null=True, verbose_name='Файл')
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Файлы"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.file.name

class Images(models.Model):

    image = models.ImageField(upload_to=generate_student_filename, blank=True, null=True, verbose_name='Изображение')
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Изображения"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.file.name


class Class(models.Model):
    name = models.CharField(max_length=32)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def pin(self):
        return (self.pk^612345)

    def __str__(self):
        return self.name+"-"+str(self.pk^612345)

    class Meta:
        verbose_name = "Классы"
        verbose_name_plural = "Классы"

    def get_absolute_url(self):
        return reverse('classcontent_url',kwargs={'name':self.name,'pk':self.pk})

    def is_teacher(self):
        if self.teacher:
            return True
        else:
            return False


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=16)
    institution = models.CharField(max_length=64, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    classes = models.ManyToManyField(Class, verbose_name='Классы', 
         through='ProfileClass')
    last_visit = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.username+"_profile"+str(self.pk)

    class Meta:
        verbose_name = "Профили"
        verbose_name_plural = "Профили"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class ProfileClass(models.Model):
    date_join = models.DateTimeField(auto_now_add=True) 
    current_class = models.ForeignKey(Class,on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username+'_has_joined_'+self.current_class.name

    class Meta:
        verbose_name = "События"
        verbose_name_plural = "События"
