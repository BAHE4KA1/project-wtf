from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import *


def index(request):
    if request.method == 'POST' and request.POST.get('logout') is not None:
        logout(request)
        return redirect('/')

    u = None
    if request.user.is_authenticated:
        u = request.user
    q = Team.objects.all()
    teams = []
    for i in q:
        teams.append({'id': i.id, 'name': i.name, 'status': i.status, 'description': i.description, 'members': i.get_members(), 'links': i.get_links()})
    return render(request, 'example.html', {'teams': teams, 'u': u})


def team_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        description = request.POST.get('description')
        logo = request.POST.get('logo')
        members = []
        for i in range(1, 6):
            members.append(f'{request.POST.get(f"member-{i}")}')
        members = ', '.join(members)
        links = []
        for i in range(1, 6):
            links.append(f'{request.POST.get(f"link-{i}")}')
        links = ', '.join(links)
        team = Team(name=name, status=status, description=description, logo=logo, team_members=members, links=links)
        try:
            team.save()
            return render(request, 'example.html', {'message': 'Команда успешно создана'})
        except:
            return render(request, 'team_add.html', {'error': 'Ошибка при создании команды'})
    return render(request, 'team_add.html')


def reg(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserAccount.create_user(username=email, password=password)
            user.save()
            return redirect('login/')
        except Exception as e:
            return render(request, 'reg.html', {'e': e})
    return render(request, 'reg.html')


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'e': 'Неправильный логин или пароль'})
    return render(request, 'login.html')