from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone, dateformat
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView

from .forms import *
from .models import *


def decode(pin):
    return int(pin) ^ 612345


@login_required
def homepage(request):
    user_classes = request.user.profile.classes
    data = []
    for el in user_classes.all():
        class_data = dict()
        class_data['class'] = el
        class_data['last_task'] = Task.objects.filter(current_class=el).order_by('-id')[0]
        data.append(class_data)
    return render(request, 'homepage.html', {
        'data': data,
    })


def sign_up(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        password_form = PasswordForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid() and password_form.is_valid():
            profile_user = User.objects.create_user(
                username=user_form.cleaned_data['email'],
                email=user_form.cleaned_data['email'],
                first_name=user_form.cleaned_data['first_name'],
                last_name=user_form.cleaned_data['last_name'],
            )
            profile_user.set_password(password_form.cleaned_data.get("password"))
            profile_user.save()
            profile = profile_form.save(commit=False)
            profile.user = profile_user
            profile.last_visit = timezone.now()
            profile.save()
            return redirect('/accounts/sign_in')
    else:
        user_form = UserForm()
        password_form = PasswordForm()
        profile_form = ProfileForm()
    return render(request, 'sign_up.html', {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form
    })


def sign_in(request):
    if request.method == "POST":
        sign_in_form = SignInForm(request.POST)
        if sign_in_form.is_valid():
            email = sign_in_form.cleaned_data.get('email')
            password = sign_in_form.cleaned_data.get('password')
            user = auth.authenticate(username=email, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect('/')
    else:
        sign_in_form = SignInForm()
    return render(request, 'sign_in.html', {
        'sign_in_form': sign_in_form,
    })


@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    marks = reversed(StudentAnswer.objects.filter(author=request.user.profile).exclude(mark=None))
    return render(request, 'profile.html', {
        'profile': profile,
        'marks': marks,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/im')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def marks(request):
    table = []
    user_classes = request.user.profile.classes
    for current_class in user_classes.all():
        table.append({'class':current_class.name, 'marks': StudentAnswer.objects.filter(current_class=current_class, author = request.user.profile).exclude(mark=None)})
    print(table)
    return render(request, 'profile_marks.html', {
        'table': table,
    })


@login_required
def class_view(request, name, pk):
    current_class = get_object_or_404(Class, pk=pk)
    is_teacher = False
    if current_class.teacher == request.user:
        is_teacher = True
    return render(request, 'class_view.html', {
        'class': current_class,
        'is_teacher': is_teacher,
    })


@login_required
def class_tasks(request, name, pk):
    current_class = get_object_or_404(Class, pk=pk)
    tasks = Task.objects.filter(current_class=current_class).order_by('-published_date')
    is_teacher = False
    if request.user == current_class.teacher:
        is_teacher = True
    return render(request, 'class_tasks.html', {
        'class': current_class,
        'tasks': tasks,
        'is_teacher': is_teacher
    })


@login_required
def class_task_view(request, name, pk, pin):
    if request.method == "POST":
        form = StudentAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            task = get_object_or_404(Task, pk=decode(pin))
            answer.task = task
            answer.current_class = get_object_or_404(Class, pk=pk)
            answer.author = request.user.profile
            answer.send_time = timezone.now()
            answer.edit_time = timezone.now()
            answer.save()
            for f in request.FILES.getlist('files'):
                f1 = Files(task=task, file=f, student_answer=answer, is_student_file=True)
                f1.save()
            for i in request.FILES.getlist('images'):
                i1 = Images(task=task, image=i, student_answer=answer, is_student_file=True)
                i1.save()
            return redirect('/classes/' + name + '-' + str(pk) + '/task=' + str(pin))
    else:
        current_class = get_object_or_404(Class, pk=pk)
        task = get_object_or_404(Task, pk=decode(pin))
        files = Files.objects.filter(task=task, is_student_file=False)
        images = Images.objects.filter(task=task, is_student_file=False)
        try:
            answer = StudentAnswer.objects.get(task=task, author=request.user.profile)
            form = StudentAnswerForm(instance=answer)
            file_form = FileForm()
            answer_exist = True
        except StudentAnswer.DoesNotExist:
            answer = None
            form = StudentAnswerForm()
            file_form = FileForm()
            answer_exist = False
        if request.user == current_class.teacher:
            is_teacher = True
        else:
            is_teacher = False
        return render(request, 'class_task_view.html', {
            'class': current_class,
            'task': task,
            'files': files,
            'images': images,
            'form': form,
            'file_form': file_form,
            'answer_exist': answer_exist,
            'is_teacher': is_teacher,
            'answer': answer,
        })


@login_required()
def class_task_answer_edit(request,  name, pk, pin):
    task = get_object_or_404(Task, pk=decode(pin))
    if request.method == "POST":
        form = StudentAnswerForm(request.POST,
                                 instance=get_object_or_404(StudentAnswer, task=task, author=request.user.profile))
        if form.is_valid():
            answer = form.save(commit=False)
            answer.edit_time = timezone.now()
            answer.save()
            existed_files = Files.objects.filter(student_answer=answer, is_student_file=True)
            for f in existed_files:
                f.delete()
            existed_images = Images.objects.filter(student_answer=answer, is_student_file=True)
            for i in existed_images:
                i.delete()
            for f in request.FILES.getlist('files'):
                f1 = Files(task=task, file=f, student_answer=answer, is_student_file=True)
                f1.save()
            for i in request.FILES.getlist('images'):
                i1 = Images(task=task, image=i, student_answer=answer, is_student_file=True)
                i1.save()
            return redirect('/classes/' + name + '-' + str(pk) + '/task=' + str(pin))


@login_required()
def class_task_add(request, name, pk):
    current_class = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = TaskAdd(request.POST)
        if form.is_valid():
            # сохраняю задание
            task = form.save(commit=False)
            task.current_class = get_object_or_404(Class, pk=pk)
            task.author = task.current_class.teacher
            task.save()
            # сохраняю материалы задания
            files = request.FILES.getlist('files')
            images = request.FILES.getlist('images')
            for f in files:
                fl = Files(task=task, file=f)
                fl.save()
            for i in images:
                im = Images(task=task, image=i)
                im.save()
            print(current_class.get_absolute_url_tasks)
            return redirect(current_class.get_absolute_url_tasks())
    else:
        form = TaskAdd()
        file_form = FileForm()
        return render(request, 'class_task_add.html', {
            'class': current_class,
            'form': form,
            'file_form': file_form,
        })


@login_required()
def class_task_delete(request, name, pk, pin):
    current_class = get_object_or_404(Class, pk=pk)
    task = get_object_or_404(Task, pk=decode(pin))
    task.delete()
    return redirect(current_class.get_absolute_url_tasks())


@login_required
def class_task_edit(request, name, pk, pin):
    task = get_object_or_404(Task, pk=decode(pin))
    if request.method == 'POST':
        form = TaskAdd(request.POST, instance=task)
        files = request.FILES.getlist('files')
        images = request.FILES.getlist('images')
        print(files, images)
        if form.is_valid():
            form.save()
            existed_files = Files.objects.filter(task=task, is_student_file=False)
            for f in existed_files:
                f.delete()
            existed_images = Images.objects.filter(task=task, is_student_file=False)
            for i in existed_images:
                i.delete()
            for f in files:
                f1 = Files(task=task, file=f)
                f1.save()
            for i in images:
                i1 = Images(task=task, image=i)
                i1.save()
            return redirect(task.get_absolute_url())
    current_class = get_object_or_404(Class, pk=pk)
    files = Files.objects.filter(task=task)
    images = Images.objects.filter(task=task)
    form = TaskAdd(instance=task)
    file_form = FileForm()
    return render(request, 'class_task_edit.html', {
        'class': current_class,
        'form': form,
        'task': task,
        'file_form': file_form,
        #'files': files,
        #'images': images,
    })


@login_required
def class_task_answers(request, name, pk, pin):
    current_class = get_object_or_404(Class, pk=pk)
    task = get_object_or_404(Task, pk=decode(pin))
    answers = reversed(StudentAnswer.objects.filter(task=task))
    return render(request, 'class_task_answers.html', {
        'class': current_class,
        'answers': answers,
        'task': task,
    })


@login_required
def class_task_answer_view(request, name, pk, pin, answer_pk):
    answer = get_object_or_404(StudentAnswer, pk=answer_pk)
    if request.method == "POST":
        form = StudentAnswerMarkForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.mark_time = timezone.now()
            answer.save()
            return redirect(answer.task.get_absolute_url_answers())
    task = get_object_or_404(Task, pk=decode(pin))
    current_class = get_object_or_404(Class, pk=pk)
    files = Files.objects.filter(student_answer=answer, is_student_file=True)
    images = Images.objects.filter(student_answer=answer, is_student_file=True)
    form = StudentAnswerMarkForm()
    return render(request, 'class_task_answer_view.html', {
        'answer': answer,
        'task': task,
        'class': current_class,
        'files': files,
        'images': images,
        'form': form,
    })


@login_required
def class_students(request, name, pk):
    current_class = get_object_or_404(Class, pk=pk)
    # Костыль для отображения в алфавитном порядке
    users = User.objects.all().order_by('last_name')
    students = []
    for i in users:
        if current_class in i.profile.classes.all():
            students.append(i)
    return render(request, 'class_students.html', {
        'class': current_class,
        'students': students,
    })


@login_required
def class_join(request):
    if request.method == "POST":
        class_join_form = ClassJoin(request.POST)
        if class_join_form.is_valid():
            pin = class_join_form.cleaned_data['pin']
            try:
                current_class = get_object_or_404(Class, pk=decode(pin))
                request.user.profile.classes.add(current_class)
                return redirect('/im')
            except Class.DoesNotExist:
                print("Неверный pin")
    else:
        class_join_form = ClassJoin()
    return render(request, 'class_join.html', {
        'class_join_form': class_join_form,
    })


@login_required
def class_leave(request, name, pk):
    request.user.profile.classes.remove(get_object_or_404(Class, pk=pk))
    return redirect('/im')


@login_required
def class_create(request):
    if request.method == "POST":
        class_create_form = ClassCreate(request.POST)
        if class_create_form.is_valid():
            current_class = class_create_form.save(commit=False)
            current_class.teacher = request.user
            current_class.save()
            request.user.profile.classes.add(current_class)
            return redirect('/im')
    else:
        class_create_form = ClassCreate()
    return render(request, 'class_create.html', {
        'class_create_form': class_create_form,
    })
