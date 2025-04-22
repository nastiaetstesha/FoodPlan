from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    is_subscribed = models.BooleanField(default=False)
    diet_preferences = models.JSONField(default=list, blank=True)  # Пример: ["vegan", "gluten_free"]


class Ingredient(models.Model):
    PRICE_RANGES = [
        ('low', 'до 50 руб'),
        ('medium', '50–150 руб'),
        ('high', '150–300 руб'),
        ('premium', '300+ руб'),
    ]

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)  # Например: гр, мл, шт
    price_range = models.CharField(max_length=10, choices=PRICE_RANGES)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
    ]

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    is_active = models.BooleanField(default=True)
    diet_tags = models.JSONField(default=list, blank=True)  # Пример: ["vegan", "eco", "gluten_free"]

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
        )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()  # Количество в единицах (граммы, мл и т.п.)

    def __str__(self):
        return f"{self.ingredient.name} для {self.recipe.title}"


class DailyMenu(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    breakfast = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='breakfast_menus'
        )
    lunch = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lunch_menus'
        )
    dinner = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dinner_menus'
        )

    def __str__(self):
        return f"Меню на {self.date}"


class UserRecipeFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    liked = models.BooleanField()  # True = лайк, False = дизлайк

    class Meta:
        unique_together = ('user', 'recipe')


class UserRecipeChoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=Recipe.MEAL_TYPES)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    swap_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date', 'meal_type')


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def total_price(self):
        return sum(item.estimated_price for item in self.items.all())

    def __str__(self):
        return f"Список покупок {self.user.username} на {self.date}"


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items'
        )
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    estimated_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} — {self.quantity} — {self.estimated_price}₽"
