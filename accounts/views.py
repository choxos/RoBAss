from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Create Account'
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                # Redirect to next URL or dashboard
                next_url = request.GET.get('next', 'assessments:dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'accounts/login.html', context)


@login_required
def profile_view(request):
    """User profile view and edit"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'title': 'My Profile'
    }
    return render(request, 'accounts/profile.html', context)


class CustomLogoutView(LogoutView):
    """Custom logout view with message"""
    next_page = reverse_lazy('assessments:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)
