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
	return render(request, 'homepage.html')


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
	return render(request,'sign_up.html',{
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
	return render(request,'sign_in.html',{
		'sign_in_form': sign_in_form,
		})


@login_required
def profile(request):
	profile = Profile.objects.get(user=request.user)
	return render(request, 'profile.html', {
		'profile': profile
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
def class_view(request, name, pk):
	current_class = Class.objects.get(pk=pk)
	return render(request, 'class_view.html', {
		'class': current_class,
		})


@login_required
def class_tasks(request, name, pk):
	current_class = Class.objects.get(pk=pk)
	tasks = Task.objects.filter(current_class=current_class).order_by('-published_date')
	return render(request, 'class_tasks.html', {
		'class': current_class,
		'tasks': tasks,
		})


@login_required
def class_task_view(request, name, pk, pin):
	if request.method == "POST":
		form = StudentAnswerForm(request.POST, request.FILES)
		if form.is_valid():
			answer = form.save(commit=False)
			task = get_object_or_404(Task, pk=decode(pin))
			answer.task = task
			answer.author = request.user.profile
			answer.save()
			for f in request.FILES.getlist('files'):
				f1 = Files(task=task, file=f, student_answer=answer, is_student_file=True)
				f1.save()
			for i in request.FILES.getlist('images'):
				i1 = Images(task=task, image=i, student_answer=answer, is_student_file=True)
				i1.save()
			return redirect('/classes/'+name+'-'+str(pk)+'/task='+str(pin))
	else:
		current_class = Class.objects.get(pk=pk)
		task = Task.objects.get(pk=decode(pin))
		files = Files.objects.filter(task=task, is_student_file=False)
		images = Images.objects.filter(task=task, is_student_file=False)
		form = StudentAnswerForm()
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
			'is_teacher': is_teacher,
		})


class TaskView(FormView):
	form_class = TaskAdd
	template_name = 'class_task_add.html'
	success_url = '/'

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		files = request.FILES.getlist('files')
		images = request.FILES.getlist('images')
		if form.is_valid():
			task = form.save(commit=False)
			task.current_class = get_object_or_404(Class, pk=kwargs['pk'])
			task.author = task.current_class.teacher
			task.save()
			for f in files:
				fl = Files(task=task, file=f)
				fl.save()
			for i in images:
				im = Images(task=task, image=i)
				im.save()
			return redirect('/classes/'+kwargs['name']+'-'+str(kwargs['pk'])+'/tasks')
		else:
			return self.form_invalid(form)


@login_required
def class_task_edit(request, name, pk, pin):
	if request.method == 'POST':
		pass
	else:
		task = Task.objects.get(pk=decode(pin))
		files = Files.objects.filter(task=task)
		images = Images.objects.filter(task=task)
		form = TaskAdd(instance=task)
		return render(request, 'class_task_add.html', {
			'form': form,
			'edit': True,
		})


@login_required
def class_students(request, name, pk):
	current_class = get_object_or_404(Class, pk=pk)
	#Костыль для отображения в алфавитном порядке
	users = User.objects.all().order_by('last_name')
	students = []
	for i in users:
		if current_class in i.profile.classes.all():
			students.append(i)
	return render(request,'class_students.html', {
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
				current_class = Class.objects.get(pk=decode(pin))
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
