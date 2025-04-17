from django.urls import path, include
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('questions/', views.question_list, name='question_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]