from django.contrib import admin
from .models import Recipe, Comment, Favorite

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'cuisine', 'cooking_time', 'created_at']
    list_filter = ['cuisine', 'created_at']
    search_fields = ['title', 'ingredients', 'author__username']
    inlines = [CommentInline, FavoriteInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'recipe', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username', 'recipe__title']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'recipe__title']