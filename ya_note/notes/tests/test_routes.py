from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Young философ')
        cls.reader = User.objects.create(username='Читатель философ')
        cls.client_author = Client()
        cls.client_reader = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(title='Title',
                                       text='Text',
                                       slug='Slug',
                                       author=cls.author)

    def test_main_page_availability_for_anonymos(self):
        """Главная страница доступна анонимному пользователю."""
        url = self.HOME_URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_users_for_done_and_add(self):
        """
        Аутентифицированному пользователю доступна
        страницы: notes/, done/, add/.
        """
        for name in ('notes:add', 'notes:success', 'notes:list'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Если попытается зайти другой пользователь — вернётся ошибка 404."""
        users_statuses = (
            (self.client_author, HTTPStatus.OK),
            (self.client_reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ('notes:edit',
                         'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug, ))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        login_url = reverse('users:login')
        for name, args in (('notes:edit', (self.note.slug, )),
                           ('notes:delete', (self.note.slug, )),
                           ('notes:success', None),
                           ('notes:list', None),
                           ('notes:add', None),
                           ('notes:detail', (self.note.slug, ))):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_user_login_logout_signup(self):
        """
        Страницы регистрации пользователей, входа в учётную запись
        и выхода из неё доступны всем пользователям.
        """
        for name in ('users:login',
                     'users:logout',
                     'users:signup'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
