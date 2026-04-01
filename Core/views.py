from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistroForm
from .models import MembroProjeto

def home(request):
    if request.user.is_authenticated:
        membros = MembroProjeto.objects.filter(usuario=request.user).select_related('projeto')
        projetos = [m.projeto for m in membros]
        return render(request, 'Core/dashboard.html', {'projetos': projetos})
    else:
        return render(request, 'Core/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Core:home')
        else:
            return render(request, 'Core/login.html', {'error': 'E-mail ou matrícula incorretos.'})
    else:
        return render(request, 'Core/login.html')

def logout_view(request):
    logout(request)
    return redirect('Core:home')

def register_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(request, username=user.email, password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('Core:home')
        else:
            return render(request, 'Core/registrar.html', {'form': form})
    else:
        form = RegistroForm()
        return render(request, 'Core/registrar.html', {'form': form})