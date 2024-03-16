from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, arg',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('get_news_id'))
    )
)
def test_home_page_avaiblity_for_user(client, name, arg):
    """
    Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    """
    url = reverse(name, args=arg)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_edit_and_delete_author_news(author_client, comments, name):
    """
    Страницы удаления и редактирования
    комментария доступны автору комментария.
    """
    url = reverse(name, args=(comments.id, ))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


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


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_user_cant_edit_delete_authors_comment(not_author_client,
                                               comments,
                                               name):
    """
    Авторизованный пользователь не может зайти на
    страницы редактирования или удаления чужих
    комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comments.id, ))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('users:logout', 'users:login', 'users:signup')
)
def test_anonymos_can_register_login_logout(client, name):
    """
    Страницы регистрации пользователей,
    входа в учётную запись и выхода из неё
    доступны анонимным пользователям.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
