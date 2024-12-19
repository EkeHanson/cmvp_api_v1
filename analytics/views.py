from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import SiteAnalytics

class SiteAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]  # Super admin check in permission

    def get(self, request):
        analytics_data = SiteAnalytics.objects.all()  # Add filters as needed
        return Response(analytics_data)
