from datetime import timedelta as td
from django.utils import timezone
from django.conf import settings
from django.db.models.expressions import F    
from .models import Profile 


def SetLastVisitMiddleware(get_response):
	def middleware(request):
		response = get_response(request)
		key = "last-activity"
		if request.user.is_authenticated:
			last_activity = request.session.get(key)
			profile = Profile.objects.get(user=request.user)
			profile.last_activity=timezone.now()
			profile.save()
			request.session[key] = timezone.now().isoformat()
		return response
	return middleware

