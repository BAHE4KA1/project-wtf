from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import *


# Главная
def index(request):
    u = None
    if request.user.is_authenticated:
        u = request.user

    if request.method == 'POST' and request.POST.get('logout') is not None:
        logout(request)
        return redirect('/')
    elif request.POST.get('delete') is not None:
        UserAccount.objects.get(id=u.id).delete_user()

    q = Team.objects.all()
    teams = []
    for i in q:
        teams.append({'id': i.id, 'name': i.name, 'status': i.status, 'description': i.description, 'members': i.get_members(), 'links': i.get_links()})
    return render(request, 'example.html', {'teams': teams, 'u': u})


# Команды
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
        for i in range(1, 11):
            links.append(f'{request.POST.get(f"link-{i}")}')
        links = ', '.join(links)

        team = Team(name=name, status=status, description=description, logo=logo, team_members=members, links=links)
        try:
            team.save()
            return render(request, 'example.html', {'message': 'Команда успешно создана'})
        finally:
            return render(request, 'team_add.html', {'error': 'Ошибка при создании команды'})
    return render(request, 'team_add.html')


def team_edit(request):
    # TODO: this
    pass


def team_delete(request):
    # TODO: this
    pass


# User interface
def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if UserAccount.objects.filter(email=email).first() is not None:
            return render(request, 'reg.html', {'e': 'Этот email уже зарегистрирован'})
        try:
            UserAccount.create_user(password=password)
            return redirect('/login/')
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


def delete_user(request):
    # TODO: this
    pass


# Profile interface
# TODO: Объединить set_id() с профилем
def set_id(request):
    if not request.user.is_authenticated:
        return render(request, 'custom_id.html', {'current': 'Сначала нужно войти в аккаунт'})

    u = request.user
    uq = SiteProfile.objects.get(id=u.id)

    if request.method == 'POST':
        new_id = request.POST.get('id_input')
        try:
            uq.set_custom_id(new_id)
            uq.save()
            return render(request, 'custom_id.html', {'error': f'ID успешно изменён. Новый ID: {uq.app_id}', 'current': uq.app_id})
        except Exception as e:
            return render(request, 'custom_id.html', {'error': e, 'current': uq.app_id})
    return render(request, 'custom_id.html', {'current': uq.app_id})


def get_users(request):
    profiles = SiteProfile.objects.all()
    return render(request, 'users.html', {'profiles': profiles})


def get_user(request, app_id: str):
    profile = SiteProfile.objects.get(app_id=app_id)
    links = profile.get_links()
    teams = profile.get_teams()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        if not full_name:
            full_name = profile.full_name

        do_search = request.POST.get('search_status')
        description = request.POST.get('description')
        stack = request.POST.get('stack')
        links = []
        for i in range(1, 11):
            links.append(f'{request.POST.get(f"link-{i}")}')
        links = ', '.join(links)

        if do_search == 'on':
            do_search = 'active'
        else:
            do_search = 'inactive'

        profile.patch(id=profile.id, app_id=profile.app_id, full_name=full_name, description=description, stack=stack, links=links, do_search=do_search)

        return redirect(f'/users/{profile.app_id}/')

    if profile.id == request.user.id:

        if profile.do_search == 'active':
            search_status = 'on'
        else:
            search_status = None

        return render(request, 'profile.html', {'profile': profile, 'search_status': search_status})

    return render(request, 'user.html', {'profile': profile, 'links': links, 'teams': teams})

# def room(request, room_name):
#     return render(request, 'chat/room.html', {
#         'room_name': room_name
#     })
