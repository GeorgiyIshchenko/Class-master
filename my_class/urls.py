from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import *

app_name="my_class"

urlpatterns = [
	path('',homepage),
	path('accounts/sign_up/',sign_up),
	path('accounts/sign_in/',sign_in),
	path('im/',profile),
	path('edit/',edit_profile),
	path('classes/join/', class_join),
	path('classes/create', class_create),
	path('classes/leave', class_leave),
	path('classes/<str:name>-<int:pk>/feed', class_view, name='classcontent_url'),
	path('classes/<str:name>-<int:pk>/tasks', class_tasks),
	path('classes/<str:name>-<int:pk>/task=<int:pin>', class_task_view),
	path('classes/<str:name>-<int:pk>/students', class_students),
	path('classes/<str:name>-<int:pk>/task_add', TaskView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)