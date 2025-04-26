"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from recipe_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("lk/", views.lk, name="lk"),
    path("order/", views.order, name="order"),
    path("registration/", views.registration, name="registration"),
    path("admin/", admin.site.urls),
    path("recipe/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path('shopping-list/<int:recipe_id>/', views.shopping_list, name='shopping_list'),
    path('recipe/<int:recipe_id>/feedback/', views.recipe_feedback, name='recipe_feedback'),
    path('lk/', views.profile, name='profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
