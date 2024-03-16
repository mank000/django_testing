from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='OtherHuman')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {'title': 'title2',
                         'text': 'text2',
                         'slug': 'slug2'}

    def test_anon_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_anon_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{reverse("notes:success")}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_not_double_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.auth_client.post(self.url, data=self.form_data)
        self.auth_client.post(self.url, data={'title': 'title3',
                                              'text': 'text3',
                                              'slug': 'slug2'})
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auto_slug(self):
        """
        Если при создании заметки не заполнен slug, то он
        формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.auth_client.post(self.url, data={'title': 'title3',
                                              'text': 'text3'})
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create(username='Author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user_author)
        cls.user_wathcer = User.objects.create(username='watcher')
        cls.watcher_client = Client()
        cls.watcher_client.force_login(cls.user_wathcer)
        cls.note = Note.objects.create(title='Title',
                                       text='Text',
                                       slug='Slug',
                                       author=cls.user_author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect = reverse('notes:success')

    def test_user_can_delete(self):
        """
        Пользователь может редактировать и
        удалять свои заметки, но не может
        редактировать или удалять чужие.
        """
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_not_user_cant_delete(self):
        """
        Пользователь может редактировать и
        удалять свои заметки, но не может
        редактировать или удалять чужие.
        """
        response = self.watcher_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_author_can_edit(self):
        response = self.auth_client.post(self.edit_url,
                                         data={"title": 'Title',
                                               "text": 'asd',
                                               "slug": 'Slug'})
        self.assertRedirects(response, self.redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, "asd")

    def test_no_user_author_cant_edit(self):
        response = self.watcher_client.post(self.edit_url,
                                            data={"title": 'Title',
                                                  "text": 'asd',
                                                  "slug": 'Slug'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
