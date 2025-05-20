from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'polls'

urlpatterns = [
    # Адмін посилання
    path('manager/recipes/', views.admin_recipe_list, name='admin_recipe_list'),
    path('manager/users/', views.admin_user_list, name='admin_user_list'),
    path('manager/comments/', views.admin_comment_list, name='admin_comment_list'),
    path('manager/users/<int:user_id>/change-password/', views.admin_change_password, name='admin_change_password'),
    path('manager/comments/<int:comment_id>/delete/', views.admin_comment_delete, name='admin_comment_delete'),


    # Основні сторінки
    path('', views.home_view, name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),

    # Аутентифікація
    path('register/', views.register_view, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),

    # Робота з рецептами
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/create/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:recipe_id>/delete/', views.recipe_delete, name='recipe_delete'),

    # Обрані рецепти
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('recipe/<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),

    # Фільтрація рецептів
    path('recipes/cuisine/<str:cuisine>/', views.recipes_by_cuisine, name='recipes_by_cuisine'),
    path('my-recipes/', views.user_recipes, name='user_recipes'),

    # Коменарі
    path('comment/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),


]