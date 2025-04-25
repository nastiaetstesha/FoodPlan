from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class User(AbstractUser):
    is_subscribed = models.BooleanField(default=False)
    diet_preferences = models.JSONField(
        default=list, blank=True
    )  # Пример: ["vegan", "gluten_free"]


class FoodTag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class PriceRange(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название диапазона (например, 'До 1 000 руб')",
        unique=True,
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Минимальная цена (может быть NULL для отсутствия ограничения)",
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Максимальная цена (может быть NULL для отсутствия ограничений)",
    )

    def get_name(self):
        if self.min_price and self.max_price:
            return f"От {int(self.min_price)} до {int(self.max_price)} руб."
        elif self.min_price:
            return f"От {int(self.min_price)} руб."
        elif self.max_price:
            return f"До {int(self.max_price)} руб."
        return

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.get_name()
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        verbose_name="Стоимость, руб./ 100 г",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    caloricity = models.DecimalField(
        verbose_name="Калорийность, ккал/100 г",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    MEAL_TYPES = [
        ("breakfast", "Завтрак"),
        ("lunch", "Обед"),
        ("dinner", "Ужин"),
    ]

    title = models.CharField(max_length=255, unique=True, verbose_name="Название блюда")
    image = models.ImageField(verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    tags = models.ManyToManyField(
        FoodTag, related_name="recipes", verbose_name="Теги блюда"
    )
    sequence = models.TextField(blank=True, verbose_name="Пошаговая инструкция")
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPES,
        verbose_name="Прием пищи",
        default="breakfast",
    )
    premium = models.BooleanField(
        default=False, verbose_name="Для премиум-пользователей"
    )
    price = models.DecimalField(
        verbose_name="Итоговая стоимость, руб.",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    mass = models.DecimalField(
        verbose_name="Масса, г.",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    calories = models.DecimalField(
        verbose_name="Общая калорийность, ккал",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )

    def get_price(self):
        for recipe_ingredient in self.ingredients.all():
            price += recipe_ingredient.ingredient.price * recipe_ingredient.mass / 100
        return price

    def get_mass(self):
        for recipe_ingredient in self.ingredients.all():
            mass += recipe_ingredient.mass
        return mass

    def get_calories(self):
        for recipe_ingredient in self.ingredients.all():
            calories += (
                recipe_ingredient.ingredient.mass
                * recipe_ingredient.ingredient.caloricity
                / 100
            )
        return calories

    def __str__(self):
        return f"{self.title} - {"Премиум" if self.premium else ""}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    mass = models.DecimalField(
        verbose_name="Масса в г",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )  # Для единообразия пусть все будет в граммах

    def __str__(self):
        return f"{self.recipe.title}: {self.ingredient.name}, {self.mass} г"


class DailyMenu(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    breakfast = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name="breakfast_menus",
    )
    lunch = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, null=True, related_name="lunch_menus"
    )
    dinner = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, null=True, related_name="dinner_menus"
    )

    def __str__(self):
        return f"Меню на {self.date}"


class UserRecipeFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    liked = models.BooleanField()  # True = лайк, False = дизлайк

    class Meta:
        unique_together = ("user", "recipe")


class UserRecipeChoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=Recipe.MEAL_TYPES)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "date", "meal_type")


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def total_price(self):
        return sum(item.estimated_price for item in self.items.all())

    def __str__(self):
        return f"Список покупок {self.user.username} на {self.date}"


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    estimated_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} — {self.quantity} — {self.estimated_price}₽"
