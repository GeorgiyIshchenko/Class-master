from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
	path('', homepage),
	path('accounts/sign_up/', sign_up),
	path('accounts/sign_in/', sign_in),
	path('im/', profile),
	path('im/marks', marks),
	path('edit/', edit_profile),
	path('classes/join/', class_join),
	path('classes/create', class_create),
	path('classes/leave', class_leave),
	path('classes/<str:name>-<int:pk>/', class_view, name='class-view'),
	path('classes/<str:name>-<int:pk>/feed', class_view, name='feed'),
	path('classes/<str:name>-<int:pk>/tasks', class_tasks, name='tasks'),
	path('classes/<str:name>-<int:pk>/task=<int:pin>/', class_task_view, name='task-view'),
	path('classes/<str:name>-<int:pk>/task_add', class_task_add, name='task-add'),
	path('classes/<str:name>-<int:pk>/task=<int:pin>/edit', class_task_edit, name='task-edit'),
	path('classes/<str:name>-<int:pk>/task=<int:pin>/delete', class_task_delete, name='task-delete'),
	path('classes/<str:name>-<int:pk>/task=<int:pin>/answers', class_task_answers, name='task-answers'),
	path('classes/<str:name>-<int:pk>/task=<int:pin>/answers/<int:answer_pk>', class_task_answer_view, name='answer-view'),
	path('classes/<str:name>-<int:pk>/students', class_students, name='students'),
	path('classes/<str:name>-<int:pk>/leave', class_leave, name='leave'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)