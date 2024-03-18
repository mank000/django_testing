from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
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
        before_post = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(before_post, notes_count)

    def test_not_anon_can_create_note(self):
        before_post = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{reverse("notes:success")}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, before_post + 1)
        note = Note.objects.last()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_not_double_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        before_post = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data={'title': 'title3',
                                                         'text': 'text3',
                                                         'slug': 'slug2'})
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, before_post + 1)
        self.assertFormError(response, 'form', 'slug',
                             f'{self.form_data["slug"]}{WARNING}')

    def test_auto_slug(self):
        """Автоматическое создание slug."""
        notes_count = Note.objects.count()
        self.auth_client.post(self.url, data={'title': 'title3',
                                              'text': 'text3'})
        after = Note.objects.count()
        latest_note = Note.objects.last()
        expected_slug = slugify(latest_note.title)
        self.assertEqual(latest_note.slug, expected_slug)
        self.assertEqual(notes_count + 1, after)


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
        cls.data = {"title": 'Title12',
                    "text": 'Tex4t',
                    "slug": 'Slug'}

    def test_user_can_delete(self):
        """Пользователь может удалять."""
        before_post = Note.objects.count()
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect)
        note_count = Note.objects.count()
        self.assertEqual(note_count, before_post - 1)

    def test_not_user_cant_delete(self):
        """Не автор не может удалять."""
        before = Note.objects.count()
        response = self.watcher_client.delete(self.delete_url)
        after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(before, after)

    def test_user_author_can_edit(self):
        response = self.auth_client.post(self.edit_url,
                                         data=self.data)
        self.assertRedirects(response, self.redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.data['text'])
        self.assertEqual(self.note.slug, self.data['slug'])
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.author, get_user(self.auth_client))

    def test_no_user_author_cant_edit(self):
        response = self.watcher_client.post(self.edit_url,
                                            data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(slug=self.data['slug'])
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.title, note.title)
        self.assertNotEqual(self.note.author, get_user(self.watcher_client))
