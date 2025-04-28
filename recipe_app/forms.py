from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserPage, MenuType, FoodTag
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class LoginForm(forms.Form):
    email = forms.CharField(label="Email", widget=forms.EmailInput)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserPage
        fields = ["username", "image"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("Файл слишком большой (максимум 2MB)")
            if not image.name.lower().endswith((".jpg", ".jpeg", ".png")):
                raise forms.ValidationError("Поддерживаются только JPG/PNG файлы")
        return image


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})


class OrderForm(forms.Form):
    MENU_TYPE_CHOICES = [(mt.id, mt.title) for mt in MenuType.objects.all()]

    ALLERGY_CHOICES = [(tag.id, tag.name) for tag in FoodTag.objects.all()]

    menu_type = forms.ChoiceField(
        choices=MENU_TYPE_CHOICES,
        label="Тип меню",
        widget=forms.RadioSelect(attrs={"class": "menu-type-radio"}),
    )

    months = forms.IntegerField(
        label="Срок подписки (месяцев)",
        initial=1,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        widget=forms.NumberInput(
            attrs={"min": 1, "max": 12, "class": "form-control", "id": "months-select"}
        ),
    )

    persons = forms.IntegerField(
        label="Количество персон",
        initial=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        widget=forms.NumberInput(
            attrs={"min": 1, "max": 6, "class": "form-control", "id": "persons-select"}
        ),
    )

    breakfast = forms.BooleanField(
        label="Завтраки",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input breakfast"}
        ),
    )

    lunch = forms.BooleanField(
        label="Обеды",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input lunch"}
        ),
    )

    dinner = forms.BooleanField(
        label="Ужины",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input dinner"}
        ),
    )

    dessert = forms.BooleanField(
        label="Десерты",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input dessert"}
        ),
    )

    allergies = forms.MultipleChoiceField(
        choices=ALLERGY_CHOICES,
        label="Аллергии",
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    promo_code = forms.CharField(
        label="Промокод",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "id": "promo-code"}),
    )

    def clean_months(self):
        months = self.cleaned_data["months"]
        if months < 1 or months > 12:
            raise forms.ValidationError("Срок подписки должен быть от 1 до 12 месяцев")
        return months
