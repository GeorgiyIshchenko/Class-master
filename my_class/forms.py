from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import *

class UserForm(forms.ModelForm):
	first_name = forms.CharField(label='Введите имя', widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
	last_name = forms.CharField(label='Введите фамилию', widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
	email = forms.CharField(label='Введите e-mail', widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))

	class Meta:
		model = User
		fields = ('first_name','last_name','email',)


class ProfileForm(forms.ModelForm):
	institution = forms.CharField(
		label='Укажите свое учебное заведение',
		widget=forms.TextInput(attrs={'placeholder': 'Учебное заведение'}))
	grade = forms.CharField(
		label='Укажите свой класс (курс)',
		widget=forms.TextInput(attrs={'placeholder': 'Класс (курс)'}))
	city = forms.CharField(
		label='Укажите свой город',
		widget=forms.TextInput(attrs={'placeholder': 'Город'}))

	class Meta:
		model = Profile
		fields = ('city','institution','grade',)


class PasswordForm(forms.Form):
	password = forms.CharField(
		label='Придумайте пароль',
		widget=forms.PasswordInput())


class SignInForm(forms.Form):
	email = forms.CharField(
		label='Введите e-mail', widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))
	password = forms.CharField(
		label='Введите пароль',
		widget=forms.PasswordInput())


class ClassCreate(forms.ModelForm):
	name = forms.CharField(
		label='Укажите название класса',
		widget=forms.TextInput(attrs={'placeholder': 'Класс'}))

	class Meta:
		model = Class
		fields = ('name',)


class ClassJoin(forms.Form):
	pin = forms.CharField(
		max_length=6,
		label='Введите персональный код класса',
		widget=forms.TextInput(attrs={'placeholder': 'Код класса'}))


class TaskAdd(forms.ModelForm):
	title = forms.CharField(
		label='Введите краткое описание задания',
		widget=forms.TextInput(attrs={'placeholder': 'Краткое описание'}))
	max_mark = forms.IntegerField(
		label='Введите максимальную оценку',
		widget=forms.NumberInput(attrs={'placeholder': 'Максимальная оценка'}))
	files = forms.FileField(
		label='Выберите файл для загрузки',
		widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
	images = forms.ImageField(
		label='Выберите изображение для загрузки',
		widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)


	class Meta:
		model = Task
		fields = ('title', 'body', 'date', 'max_mark')
