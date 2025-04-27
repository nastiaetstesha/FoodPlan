from django.contrib import admin
from .models import (
    User,
    FoodTag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    DailyMenu,
    UserRecipeFeedback,
    UserRecipeChoice,
    ShoppingList,
    ShoppingItem,
    PriceRange,
)
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_subscribed", "email")
    list_filter = ("is_subscribed",)


@admin.register(FoodTag)
class FoodTagAdmin(admin.ModelAdmin):
    list_display = ("name",)


<<<<<<< Updated upstream
=======
@admin.register(UserPage)
class UserPageAdmin(admin.ModelAdmin):
    list_display = ("username", "user", "is_subscribed", "all_allergies", "image_preview")
    list_editable = ("is_subscribed",)
    list_filter = ("is_subscribed",)

    def all_allergies(self, obj):
        if obj.allergies:
            return ", ".join(allergy.name for allergy in obj.allergies.all())
        return "-"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{url}" style="max-width: {max_width}px; max-height: {max_height}px; width: auto; height: auto;"/>',
                max_width=200,
                max_height=200,
                url=obj.image.url,
            )
        return format_html('<span style="color: gray;">Нет изображения</span>')

    image_preview.short_description = "Превью изображения"


>>>>>>> Stashed changes
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "price")


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    fields = ("ingredient", "mass")
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "description",
        "image_preview",
        "meal_type",
        "price",
        "premium",
        "foodtags",
    ]
    list_filter = ("meal_type", "tags", "premium")
    inlines = [RecipeIngredientInline]
    readonly_fields = ["image_preview"]
    search_fields = ("title",)

    def foodtags(self, obj):
        if obj.tags:
            return ", ".join(tag.name for tag in obj.tags.all())
        return "-"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{url}" style="max-width: {max_width}px; max-height: {max_height}px; width: auto; height: auto;"/>',
                max_width=200,
                max_height=200,
                url=obj.image.url,
            )
        return format_html('<span style="color: gray;">Нет изображения</span>')

    image_preview.short_description = "Превью изображения"


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ("date", "breakfast", "lunch", "dinner")


@admin.register(UserRecipeFeedback)
class UserRecipeFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "liked")
    list_filter = ("liked",)


@admin.register(UserRecipeChoice)
class UserRecipeChoiceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "meal_type", "recipe")


class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 0


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "total_price")
    inlines = [ShoppingItemInline]


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ("shopping_list", "name", "quantity", "estimated_price")


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ["name", "min_price", "max_price"]
    search_fields = ["name"]
