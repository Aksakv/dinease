from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from .forms import RegisterForm

# Create your views here.
class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("/accounts/login/")
    
class UserLoginView(LoginView):
    template_name = "accounts/login.html"    