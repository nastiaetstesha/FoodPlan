from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Юзеры"


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


class MenuType(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Тип меню")
    image = models.ImageField(
        upload_to="./menus/",
        verbose_name="Изображение меню",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    MEAL_TYPES = [
        ("breakfast", "Завтрак"),
        ("lunch", "Обед"),
        ("dinner", "Ужин"),
        ("dessert", "Десерт"),
    ]

    title = models.CharField(max_length=255, unique=True, verbose_name="Название блюда")
    image = models.ImageField(verbose_name="Изображение", upload_to="./recipes/")
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

    on_index = models.BooleanField(
        default=False, verbose_name="отображать на главной странице?"
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

    menu_type = models.ForeignKey(
        MenuType,
        verbose_name="Тип меню",
        on_delete=models.CASCADE,
        related_name="recipes",
        blank=True,
        null=True
    )

    def get_price(self):
        price = 0
        for ingredient in self.ingredients.all():
            if ingredient.ingredient.price and ingredient.mass:
                price += ingredient.ingredient.price * ingredient.mass / 100
        return price

    def get_mass(self):
        mass = 0
        for ingredient in self.ingredients.all():
            if ingredient.mass:
                mass += ingredient.mass
        return mass

    def get_calories(self):
        calories = 0
        for ingredient in self.ingredients.all():
            if ingredient.ingredient.caloricity and ingredient.mass:
                calories += ingredient.mass * ingredient.ingredient.caloricity / 100
        return calories

    def __str__(self):
        return f"""{self.title} - {"Премиум" if self.premium else ""}"""


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


class UserPage(models.Model):
    username = models.CharField(
        max_length=255, verbose_name="Имя", blank=True, default="Имя"
    )

    image = models.ImageField(
        upload_to="./avatars/", verbose_name="Изображение", blank=True, null=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="page",
        verbose_name="Связанный аккаунт",
    )
    is_subscribed = models.BooleanField(default=False, verbose_name="Премиум")

    allergies = models.ManyToManyField(
        FoodTag, related_name="userpages", verbose_name="Аллергии", blank=True
    )
    liked_recipes = models.ManyToManyField(
        Recipe, related_name="liked", verbose_name="Понравившиеся рецепты", blank=True
    )
    disliked_recipes = models.ManyToManyField(
        Recipe,
        related_name="disliked",
        verbose_name="Непонравившиеся рецепты",
        blank=True,
    )

    menu_type = models.ForeignKey(
        MenuType,
        related_name="users",
        verbose_name="Тип меню",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Страницы клиентов"
        ordering = ["username"]


class Subscription(models.Model): 
    base_price = models.DecimalField(
        verbose_name="Базовая стоимость подписки, руб",
        max_digits=10,
        decimal_places=2,
        default=1000.00,
        validators=[MinValueValidator(0)],
    )

    user = models.ForeignKey(
        UserPage,
        related_name="subscription",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    
    menu_type = models.ForeignKey(
        MenuType,
        related_name="subscriptions",
        verbose_name="Тип меню",
        on_delete=models.CASCADE,
    )

    months = models.PositiveIntegerField(
        verbose_name="Количество месяцев",
        validators=[
            MinValueValidator(1, message="Минимальный срок - 1 месяц"),
            MaxValueValidator(12, message="Максимальный срок - 12 месяцев (1 год)"),
        ],
        default=1,
    )
    persons = models.PositiveIntegerField(
        verbose_name="Количество персон",
        validators=[
            MinValueValidator(1, message="Минимум - 1 персона"),
            MaxValueValidator(5, message="Максимум - 5 персон"),
        ],
        default=1,
    )

    breakfast = models.BooleanField(verbose_name="Завтраки", default=True)
    lunch = models.BooleanField(verbose_name="Обеды", default=False)
    dinner = models.BooleanField(verbose_name="Ужины", default=False)
    dessert = models.BooleanField(verbose_name="Десерты", default=False)
    
    price = models.DecimalField(verbose_name="Стоимость, руб.",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    
    promocode = models.CharField(max_length=255, verbose_name="Промокод", blank=True, null=True)
    
    
    class Meta:
        verbose_name = "Подписки"
        ordering = ["user", "menu_type"]
    

class DailyMenu(models.Model):
    DAYS_OF_WEEK = [
        ("mon", "понедельник"),
        ("tue", "вторник"),
        ("wen", "среда"),
        ("thu", "четверг"),
        ("fri", "пятница"),
        ("sat", "суббота"),
        ("sun", "воскресенье"),
    ]

    menu_type = models.ForeignKey(
        MenuType,
        related_name="dailymenus",
        verbose_name="Тип меню",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    date = models.CharField(
        choices=DAYS_OF_WEEK, verbose_name="День недели", default="mon"
    )

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

    dessert = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL, null=True, related_name="dessert_menus"
    )

    users = models.ManyToManyField(
        UserPage, verbose_name="Пользователи", related_name="daily_menu", blank=True
    )

    def __str__(self):
        return f"Меню на {self.date}"
