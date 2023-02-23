import pytest
from django.test import Client
from rest_framework.exceptions import PermissionDenied

from .models import User, Team, MANAGEMENT, SALES, SUPPORT


@pytest.fixture
def client(db):
    return Client()


@pytest.fixture
def management_team(db):
    team = Team.objects.create(name=MANAGEMENT)
    return team


@pytest.fixture
def sales_team(db):
    team2 = Team.objects.create(name=SALES)
    return team2


@pytest.fixture
def support_team(db):
    team3 = Team.objects.create(name=SUPPORT)
    return team3


@pytest.fixture
def manager_user(db, management_team):
    manager = User.objects.create_user(username="manager_user", password="pwd12345",
                                       team=management_team)
    manager.is_superuser = True
    manager.is_staff = True
    manager.save()
    return manager


@pytest.fixture
def seller_user(db, sales_team):
    seller = User.objects.create_user(username="seller_user", password="pwd12345",
                                      team=sales_team)
    seller.is_superuser = False
    seller.is_staff = False
    seller.save()
    return seller


@pytest.fixture
def supporter_user(db, support_team):
    supporter = User.objects.create_user(username="supporter_user", password="pwd12345",
                                         team=support_team)
    supporter.is_superuser = False
    supporter.is_staff = False
    supporter.save()
    return supporter

# ################################################################# #
# ###################       -TEST STR-     ######################## #


def test_str_team(sales_team):
    assert str(sales_team) == "SALES"


def test_delete_team(sales_team):
    with pytest.raises(PermissionDenied):
        sales_team.delete()
# ################################################################# #
# ################## TEST connexion admin panel ################### #


def test_manager_user_on_admin(db, client, manager_user, management_team):
    client.login(username=manager_user.username, password='pwd12345')
    response = client.get('/admin/')
    assert response.status_code == 200
    client.logout()


def test_seller_user_on_admin(db, client, seller_user, sales_team):
    client.login(username=seller_user.username, password='pwd12345')
    response = client.get('/admin/')
    assert response.status_code == 302
    client.logout()


def test_supporter_user_on_admin(db, client, supporter_user, support_team):
    client.login(username=supporter_user.username, password='pwd12345')
    response = client.get('/admin/')
    assert response.status_code == 302
    client.logout()

# ################################################################# #
# ################## TEST connexion crm ################### #


# managers: #


def test_manager_login_authorized(db, client: Client, manager_user, management_team):
    data = {'username': manager_user.username, 'password': 'pwd12345'}
    response = client.post('/login/', data)
    assert response.status_code == 200


def test_manager_login_with_wrong_password(db, client: Client, manager_user, management_team):
    data = {'username': manager_user.username, 'password': 'wrong'}
    response = client.post('/login/', data)
    assert response.status_code == 401


def test_unknown_manager(db, client: Client, manager_user, management_team):
    data = {'username': 'unknown', 'password': '123'}
    response = client.post('/login/', data)
    assert response.status_code == 401


# supporters: #


def test_supporter_login_authorized(db, client: Client, supporter_user, support_team):
    data = {'username': supporter_user.username, 'password': 'pwd12345'}
    response = client.post('/login/', data)
    assert response.status_code == 200


def test_supporter_login_with_wrong_password(db, client: Client, supporter_user, support_team):
    data = {'username': supporter_user.username, 'password': 'wrong'}
    response = client.post('/login/', data)
    assert response.status_code == 401


def test_unknown_supporter(db, client: Client, supporter_user, support_team):
    data = {'username': 'unknown', 'password': '123'}
    response = client.post('/login/', data)
    assert response.status_code == 401

# sellers: #


def test_seller_login_authorized(db, client: Client, seller_user, sales_team):
    data = {'username': seller_user.username, 'password': 'pwd12345'}
    response = client.post('/login/', data)
    assert response.status_code == 200


def test_seller_login_with_wrong_password(db, client: Client, seller_user, sales_team):
    data = {'username': seller_user.username, 'password': 'wrong'}
    response = client.post('/login/', data)
    assert response.status_code == 401


def test_unknown_seller(db, client: Client, seller_user, sales_team):
    data = {'username': 'unknown', 'password': '123'}
    response = client.post('/login/', data)
    assert response.status_code == 401
