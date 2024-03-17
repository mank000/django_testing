from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, user, status',
    (
        ('news:home', pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        ('news:delete', pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        ('users:logout', pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('users:login', pytest.lazy_fixture('client'), HTTPStatus.OK),
        ('users:signup', pytest.lazy_fixture('client'), HTTPStatus.OK)
    )
)
def test_home_page_avaiblity_for_user(user, name, status, news, comments):
    """
    Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    """
    if name in ['news:detail']:
        arg = (news.id, )
    elif name in ['news:edit', 'news:delete']:
        arg = (comments.id, )
    else:
        arg = None
    url = reverse(name, args=arg)
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_not_avaible_edit_delete_for_anonymous(client, comments, name):
    """
    При попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    url = reverse(name, args=(comments.id, ))
    login_url = reverse('users:login')
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
