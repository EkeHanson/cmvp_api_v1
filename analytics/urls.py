from django.urls import path
from .views import SiteAnalyticsView

urlpatterns = [
    path('site/', SiteAnalyticsView.as_view(), name='site_analytics'),
]
