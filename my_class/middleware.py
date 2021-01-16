from datetime import timedelta as td
from django.utils import timezone
from django.conf import settings
from django.db.models.expressions import F    
from .models import Profile 

def SetLastVisitMiddleware(get_response):
	def middleware(request):
		response = get_response(request)
		if request.user.is_authenticated:
			profile = request.user.profile
			profile.last_visit = timezone.now()
			profile.save()
		return response
	return middleware
