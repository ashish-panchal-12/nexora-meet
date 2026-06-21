import traceback
import random

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import Profile

# for forgot password
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
import random


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            otp = random.randint(100000, 999999)

            request.session["otp"] = str(otp)

            request.session["user_data"] = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "password": form.cleaned_data["password1"],
                "mobile_number": form.cleaned_data.get("mobile_number", ""),
            }

            try:
                from django.conf import settings

                print("EMAIL_HOST =", settings.EMAIL_HOST)
                print("EMAIL_HOST_USER =", settings.EMAIL_HOST_USER)
                print("EMAIL_HOST_PASSWORD =", settings.EMAIL_HOST_PASSWORD)
                send_mail(
                    "Nexora Meet Verification Code",
                    f"Your OTP is: {otp}",
                    settings.DEFAULT_FROM_EMAIL,
                    [form.cleaned_data["email"]],
                    fail_silently=False,
                )

                return redirect("verify_otp")

            except Exception as e:
                print("EMAIL ERROR:", e)
                messages.error(request, f"Email Error: {e}")
            return redirect("register")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("otp")
        if entered_otp == saved_otp:
            data = request.session.get("user_data")
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
            )
            Profile.objects.create(user=user, mobile_number=data.get("mobile_number"))
            login(request, user)
            del request.session["otp"]
            del request.session["user_data"]
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid OTP")
    return render(request, "accounts/verify_otp.html")


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        login_input = request.POST.get("username")
        password = request.POST.get("password")

        user = None

        # Login using Email
        try:
            user_obj = User.objects.filter(email=login_input).first()

            if user_obj:
                user = authenticate(
                    request, username=user_obj.username, password=password
                )

        except Exception:
            pass

        # Login using Mobile Number
        if user is None:
            try:
                profile = Profile.objects.get(mobile_number=login_input)

                user = authenticate(
                    request, username=profile.user.username, password=password
                )

            except Profile.DoesNotExist:
                pass

        # Login using Username
        if user is None:
            user = authenticate(request, username=login_input, password=password)

        if user:
            login(request, user)

            messages.success(
                request, f"Welcome back, {user.first_name or user.username}!"
            )

            return redirect("dashboard")

        messages.error(request, "Invalid credentials")

    form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    hosted_count = request.user.hosted_meetings.count()
    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile,
            "hosted_count": hosted_count,
        },
    )


def forgot_password_view(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            otp = random.randint(100000, 999999)

            request.session["reset_otp"] = str(otp)
            request.session["reset_email"] = email

            send_mail(
                "Password Reset OTP",
                f"Your OTP is: {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect("verify_reset_otp")

        except User.DoesNotExist:

            messages.error(request, "No account found with this email.")

    return render(request, "accounts/forgot_password.html")


def verify_reset_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("reset_otp")

        if entered_otp == saved_otp:
            request.session["reset_verified"] = True
            return redirect("reset_password")

        messages.error(request, "Invalid OTP")

    return render(request, "accounts/verify_reset_otp.html")


def reset_password_view(request):
    if not request.session.get("reset_verified"):
        return redirect("forgot_password")

    if request.method == "POST":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:

            messages.error(request, "Passwords do not match")

            return redirect("reset_password")

        email = request.session.get("reset_email")

        user = User.objects.get(email=email)

        user.set_password(password1)

        user.save()

        request.session.pop("reset_otp", None)
        request.session.pop("reset_email", None)
        request.session.pop("reset_verified", None)

        messages.success(request, "Password changed successfully.")

        return redirect("login")

    return render(request, "accounts/reset_password.html")
