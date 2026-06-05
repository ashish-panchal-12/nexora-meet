from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('profile/',  views.profile_view,  name='profile'),
    path('verify-otp/', views.verify_otp,  name='verify_otp'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]