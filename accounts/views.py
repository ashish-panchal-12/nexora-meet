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


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            otp = random.randint(100000, 999999)

            request.session['otp'] = str(otp)

            request.session['user_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password1'],
                'mobile_number': form.cleaned_data.get('mobile_number', ''),
            }

            try:
                send_mail(
                'Nexora Meet Verification Code',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )

                return redirect('verify_otp')
        
            except Exception:
                messages.error(
                    request,
                        "Failed to send OTP email. Please try again."
            )
            return redirect('register')

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')
        if entered_otp == saved_otp:
            data = request.session.get('user_data')
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            Profile.objects.create(user=user, mobile_number=data.get('mobile_number'))
            login(request, user)
            del request.session['otp']
            del request.session['user_data']
            return redirect('dashboard')
        else:
            messages.error(
                request,
                'Invalid OTP'
            )
    return render(
        request,
        'accounts/verify_otp.html'
    )
    
    
def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        login_input = request.POST.get('username')
        password = request.POST.get('password')

        user = None

        # Login using Email
        try:
            user_obj = User.objects.get(email=login_input)
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
        except User.DoesNotExist:
            pass

        # Login using Mobile Number
        if user is None:
            try:
                profile = Profile.objects.get(
                    mobile_number=login_input
                )

                user = authenticate(
                    request,
                    username=profile.user.username,
                    password=password
                )

            except Profile.DoesNotExist:
                pass

        # Login using Username
        if user is None:
            user = authenticate(
                request,
                username=login_input,
                password=password
            )

        if user:
            login(request, user)

            messages.success(
                request,
                f'Welcome back, {user.first_name or user.username}!'
            )

            return redirect('dashboard')

        messages.error(
            request,
            'Invalid credentials'
        )

    form = LoginForm()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )
    

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name  = form.cleaned_data['last_name']
            request.user.email      = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    hosted_count = request.user.hosted_meetings.count()
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'hosted_count': hosted_count,
    })