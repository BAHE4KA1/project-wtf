from django.db import models
from django.contrib.auth.models import User


class UserAccount(models.Model):
    __tablename__ = 'profiles'
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(max_length=128, unique=True, blank=False)

    @staticmethod
    def create_user(**kwargs) -> None:
        user = User.objects.create_user(
            username=kwargs.get('email'),
            password=kwargs.get('password'),
            email=kwargs.get('email')
        )
        ua = UserAccount.objects.create(user=user, email=kwargs.get('email'))
        SiteProfile.objects.create(person_id=ua.id)

    def save(self, *args, **kwargs) -> None:
        super(UserAccount, self).save(*args, **kwargs)

    def delete_user(self) -> None:
        try:
            self.user = User.objects.filter(id=self.user.id).delete()
            SiteProfile.objects.filter(person_id=self.id).delete()
            self.delete()
        except Exception as e:
            raise e

    def __str__(self) -> str:
        return f'{self.email} ({self.id})'


class SiteProfile(models.Model):
    __tablename__ = 'site_profiles'
    id = models.AutoField(primary_key=True, blank=False, unique=True)
    app_id = models.CharField(max_length=256, blank=False, unique=True)
    person_id = models.CharField(max_length=16, blank=False, unique=True)

    search_statuses = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('suspended', 'Приостановлен'),
    ]

    full_name = models.CharField(max_length=128, blank=True)
    do_search = models.CharField(max_length=128, blank=True, choices=search_statuses)
    search_status = models.CharField(max_length=256, blank=True)

    # Добавить форму для прикрепления файла фотки, который мы будем сохранять на сервере
    logo_url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True, max_length=1024)

    # Добавить форму для ввода стека в определённом формате, где теги будут разделены запятыми и будут
    # содержать число лет опыта работы в данной области
    stack = models.CharField(max_length=1024, blank=True)

    # Добавить форму для ввода ссылок в формате нумерованного списка
    links = models.CharField(max_length=1024, blank=True)
    teams = models.CharField(max_length=1024, blank=True)  # Логика как с cart в проекте магазина

    def set_custom_id(self, new_id) -> None:
        if not SiteProfile.objects.filter(app_id=new_id).exists():
            self.app_id = new_id
            self.save()
        else:
            raise Exception('exists')

    def get_links(self) -> list:
        links_list = self.links.split(',')
        return [link.strip() for link in links_list if link.strip()]

    def add_link(self, link: str) -> str:
        if not self.links:
            self.links = link
            return 'Successfully set link'
        else:
            self.links += f', {link}'
            return 'Successfully added link'

    def remove_link(self, link: str) -> str:
        if self.links:
            links_list = self.links.split(',')
            new_links = [link.strip() for link in links_list if link.strip() != link]
            self.links = ', '.join(new_links)
            return f'Successfully removed link {link}'
        else:
            return 'No links to remove'

    def get_teams(self) -> list:
        teams_list = self.teams.split(',')
        return [team.strip() for team in teams_list if team.strip()]

    def add_team(self, team: str) -> str:
        if not self.teams:
            self.teams = team
            return 'Successfully set team'
        else:
            self.teams += f', {team}'
            return 'Successfully added team'

    def remove_team(self, team: str) -> str:
        if self.teams:
            teams_list = self.teams.split(',')
            new_teams = [team.strip() for team in teams_list if team.strip() != team]
            self.teams = ', '.join(new_teams)
            return f'Successfully removed team {team}'
        else:
            return 'No teams to remove'

    @staticmethod
    def patch(*args, **kwargs) -> None:
        SiteProfile(*args, **kwargs).save()

    def save(self, *args, **kwargs) -> None:
        if not self.description:
            self.description = 'Пользователь не предоставил описания'
        if not self.app_id:
            self.app_id = f'UnsetID_{self.id}'
        super(SiteProfile, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Site profile for {self.app_id}'


class Team(models.Model):
    __tablename__ = 'teams'
    id = models.AutoField(primary_key=True)

    statuses = [
        ('active', 'Активна'),
        ('inactive', 'Неактивна'),
        ('suspended', 'Приостановлена'),
    ]

    name = models.CharField(max_length=128, blank=False)
    status = models.CharField(max_length=128, blank=False, choices=statuses)

    # Добавить форму для прикрепления файла фотки, который мы будем сохранять на сервере
    logo = models.FileField(upload_to='team_logo', blank=True)
    logo_url = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True, max_length=1024)

    # Добавить форму для добавления участников команды с указанием роли
    team_members = models.CharField(max_length=2048, blank=False)
    links = models.CharField(max_length=1024, blank=True)

    def get_links(self) -> list:
        links_list = self.links.split(',')
        return [link.strip() for link in links_list if link.strip()]

    def add_link(self, link: str) -> str:
        if not self.links:
            self.links = link
            return 'Successfully set link'
        else:
            self.links += f', {link}'
            return 'Successfully added link'

    def remove_link(self, link: str) -> str:
        if self.links:
            links_list = self.links.split(',')
            new_links = [link.strip() for link in links_list if link.strip() != link]
            self.links = ', '.join(new_links)
            return f'Successfully removed link {link}'
        else:
            return 'No links to remove'

    def get_members(self) -> list:
        members_list = self.team_members.split(',')
        return [member.strip() for member in members_list if member.strip()]

    def add_member(self, member: str) -> str:
        if not self.team_members:
            self.team_members = member
            return 'Successfully set member'
        else:
            self.team_members += f', {member}'
            return 'Successfully added member'

    def remove_member(self, member: str) -> str:
        if self.team_members:
            members_list = self.team_members.split(',')
            new_members = [member.strip() for member in members_list if member.strip() != member]
            self.team_members = ', '.join(new_members)
            return f'Successfully removed member {member}'
        else:
            return 'No members to remove'

    def save(self, *args, **kwargs) -> None:
        if not self.description:
            self.description = 'Команда не предоставила описания'
        super(Team, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} - {self.status}'

# TODO: Менеджер пользователей
