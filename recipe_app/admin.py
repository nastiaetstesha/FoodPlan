from django.contrib import admin
from .models import (
    User, Ingredient, Recipe, RecipeIngredient,
    DailyMenu, UserRecipeFeedback, UserRecipeChoice,
    ShoppingList, ShoppingItem
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_subscribed', 'email')
    list_filter = ('is_subscribed',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'price_range')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'meal_type', 'is_active')
    list_filter = ('meal_type', 'diet_tags', 'is_active')
    search_fields = ('title',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity')


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ('date', 'breakfast', 'lunch', 'dinner')


@admin.register(UserRecipeFeedback)
class UserRecipeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'liked')
    list_filter = ('liked',)


@admin.register(UserRecipeChoice)
class UserRecipeChoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_type', 'recipe', 'swap_count')


class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 0


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_price')
    inlines = [ShoppingItemInline]


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ('shopping_list', 'name', 'quantity', 'estimated_price')
