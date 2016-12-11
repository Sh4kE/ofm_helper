from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from core.localization.messages import MSG_PASSWORDS_UNEQUAL, MSG_OFM_PASSWORDS_UNEQUAL, MSG_NOT_LOGGED_IN, \
    OFM_USERNAME_ALREADY_EXISTS, USERNAME_ALREADY_EXISTS, EMAIL_ALREADY_EXISTS, MSG_ALREADY_LOGGED_IN, \
    MSG_ACCOUNT_CREATED, LOGGED_OUT, USERNAME_OR_PASSWORD_INVALID, LOGIN_IMPOSSIBLE_ACCOUNT_IS_DEACTIVATED, \
    LOGIN_SUCCESSFUL
from users.models import OFMUser


def register_view(request):
    if request.user.is_authenticated():
        messages.error(request, MSG_ALREADY_LOGGED_IN)
        return render(request, 'core/account/home.html')
    if request.POST:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        ofm_username = request.POST.get('ofm_username')
        ofm_password = request.POST.get('ofm_password')
        ofm_password2 = request.POST.get('ofm_password2')

        if OFMUser.objects.filter(email=email).exists():
            messages.error(request, EMAIL_ALREADY_EXISTS)
            return redirect('core:register')

        if OFMUser.objects.filter(username=username).exists():
            messages.error(request, USERNAME_ALREADY_EXISTS)
            return redirect('core:register')

        if password != password2:
            messages.error(request, MSG_PASSWORDS_UNEQUAL)
            return redirect('core:register')

        if OFMUser.objects.filter(ofm_username=ofm_username).exists():
            messages.error(request, OFM_USERNAME_ALREADY_EXISTS)
            return redirect('core:register')

        if ofm_password != ofm_password2:
            messages.error(request, MSG_OFM_PASSWORDS_UNEQUAL)
            return redirect('core:register')

        OFMUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            ofm_username=ofm_username,
            ofm_password=ofm_password,
        )

        messages.success(request, MSG_ACCOUNT_CREATED)
        return redirect('core:login')

    else:
        return render(request, 'core/account/register.html')


def login_view(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, LOGIN_SUCCESSFUL)
                return render(request, 'core/account/home.html')
            else:
                messages.error(request, LOGIN_IMPOSSIBLE_ACCOUNT_IS_DEACTIVATED)
                return redirect('core:login')
        else:
            messages.error(request, USERNAME_OR_PASSWORD_INVALID)
            return redirect('core:login')
    else:
        if request.user.is_authenticated():
            return render(request, 'core/account/home.html')
        else:
            return render(request, 'core/account/login.html')


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
        messages.success(request, LOGGED_OUT)
    return redirect('core:home')


def account_view(request):
    if request.user.is_authenticated():
        return render(request, 'core/account/home.html')
    else:
        messages.error(request, MSG_NOT_LOGGED_IN)
        return redirect('core:login')
