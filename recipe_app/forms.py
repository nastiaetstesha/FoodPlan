from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserPage
from django.contrib.auth.forms import PasswordChangeForm



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
    email = forms.CharField(label='Email', widget=forms.EmailInput)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserPage
        fields = ['username', 'image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2*1024*1024:  # 2MB
                raise forms.ValidationError("Файл слишком большой (максимум 2MB)")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Поддерживаются только JPG/PNG файлы")
        return image
    
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})