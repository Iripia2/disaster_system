from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='list'),
    path('submit/', views.submit_report, name='submit'),
    path('anonymous-submit/', views.anonymous_submit_report, name='anonymous_submit'),
    path('anonymous-success/', views.anonymous_success, name='anonymous_success'),
    path('feed-data/', views.public_feed_data, name='feed_data'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_report, name='delete'),
]
