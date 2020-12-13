from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from django.shortcuts import reverse
from PIL import Image


def generate_pin(n):
    return n ^ 612345


def generate_teacher_filename(instance, filename):
    filename = instance.task.author.first_name+instance.task.author.last_name+"_на_"+str(instance.task.date)+filename
    return "{0}/{1}".format(instance.task.author.username, filename)


class Task(models.Model):
    title = models.CharField(max_length=32)
    body = RichTextUploadingField(blank=True, null=True)
    date = models.DateField()
    current_class = models.ForeignKey('Class', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    max_mark = models.IntegerField(default=5)

    def __str__(self): 
        return self.title + " | "+str(self.pk)

    def pin(self):
        return generate_pin(self.pk)

    def not_empty(self):
        if self.body == "":
            return False
        else:
            return True

    class Meta:
        verbose_name = "Задания"
        verbose_name_plural = "Задания"

    def get_absolute_url(self):
        return reverse('task-view', kwargs={'name': self.current_class.name, 'pk': self.current_class.pk,
                                            'pin': generate_pin(self.pk)})

    def get_absolute_url_edit(self):
        return reverse('task-edit', kwargs={'name': self.current_class.name, 'pk': self.current_class.pk,
                                            'pin': generate_pin(self.pk)})

    def get_absolute_url_delete(self):
        return reverse('task-delete', kwargs={'name': self.current_class.name, 'pk': self.current_class.pk,
                                              'pin': generate_pin(self.pk)})

    def get_absolute_url_answers(self):
        return reverse('task-answers', kwargs={'name': self.current_class.name, 'pk': self.current_class.pk,
                                              'pin': generate_pin(self.pk)})


class StudentAnswer(models.Model):
    comment = models.TextField(max_length=256)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    teacher_comment = models.TextField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = "Ответы"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.author.user.last_name+'_'+self.comment


class Files(models.Model):
    file = models.FileField(upload_to=generate_teacher_filename, blank=True, null=True, verbose_name='Файл')
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.CASCADE)
    student_answer = models.ForeignKey(StudentAnswer, blank=True, null=True, on_delete=models.CASCADE)
    is_student_file = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Файлы"
        verbose_name_plural = "Файлы"

    def get_name(self):
        return self.file.name.split('/')[1]

    def __str__(self):
        return self.file.name


class Images(models.Model):
    image = models.ImageField(upload_to=generate_teacher_filename, blank=True, null=True, verbose_name='Изображение')
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.CASCADE)
    student_answer = models.ForeignKey(StudentAnswer, blank=True, null=True, on_delete=models.CASCADE)
    is_student_file = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Изображения"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.image.name


class Class(models.Model):
    name = models.CharField(max_length=32)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def pin(self):
        return generate_pin(self.pk)

    def __str__(self):
        return self.name+"-"+str(self.pk^612345)

    class Meta:
        verbose_name = "Классы"
        verbose_name_plural = "Классы"

    def get_absolute_url(self):
        return reverse('class-view', kwargs={'name': self.name, 'pk': self.pk})

    def get_absolute_url_feed(self):
        return reverse('feed', kwargs={'name': self.name, 'pk': self.pk})

    def get_absolute_url_tasks(self):
        return reverse('tasks', kwargs={'name': self.name, 'pk': self.pk})

    def get_absolute_url_task_add(self):
        return reverse('task-add', kwargs={'name': self.name, 'pk': self.pk})

    def get_absolute_url_students(self):
        return reverse('students', kwargs={'name': self.name, 'pk': self.pk})

    def get_absolute_url_leave(self):
        return reverse('leave', kwargs={'name': self.name, 'pk': self.pk})


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=16)
    institution = models.CharField(max_length=64, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    classes = models.ManyToManyField(Class, verbose_name='Классы', through='ProfileClass')
    last_visit = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username+"_profile"+str(self.pk)

    def is_teacher(self):
        if len(Class.objects.filter(teacher=self.user)) > 0:
            return True
        else:
            return False

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
    current_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username+'_has_joined_'+self.current_class.name

    class Meta:
        verbose_name = "События"
        verbose_name_plural = "События"
