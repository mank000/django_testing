from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Young философ')
        cls.reader = User.objects.create(username='Читатель философ')
        cls.client_author = Client()
        cls.client_reader = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader.force_login(cls.reader)
        cls.notes_list = reverse('notes:list')
        cls.note = Note.objects.create(title='Title',
                                       text='Text',
                                       slug='Slug',
                                       author=cls.author)

    def test_object_list_on_context(self):
        """Отдельная заметка передается в списке."""
        response = self.client_author.get(self.notes_list)
        self.assertIn('note_list', response.context)
        self.assertIn(self.note, response.context['note_list'])

    def test_notes_for_one_user(self):
        """Не попадают заметки другого пользователя."""
        response = self.client_reader.get(self.notes_list)
        self.assertNotIn(self.note, response.context['note_list'])

    def test_forms_on_add_edit(self):
        """Формы на редактирование."""
        for name, args in (('notes:edit', (self.note.slug, )),
                           ('notes:add', None)):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
