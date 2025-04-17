from django.urls import path, include
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('register/', views.register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
]