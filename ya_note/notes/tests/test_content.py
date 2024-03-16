from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Young философ')
        cls.reader = User.objects.create(username='Читатель философ')
        cls.notes_list = reverse('notes:list')
        cls.note = Note.objects.create(title='Title',
                                       text='Text',
                                       slug='Slug',
                                       author=cls.author)

    def test_object_list_on_context(self):
        """
        Отдельная заметка передаётся
        на страницу со списком заметок в списке.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.notes_list)
        self.assertIn('note_list', response.context)

    def test_notes_for_one_user(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        self.client.force_login(self.reader)
        response = self.client.get(self.notes_list)
        self.assertEqual(response.context.get('note_list').count(), 0)

    def test_forms_on_add_edit(self):
        """
        На страницы создания и
        редактирования заметки передаются формы.
        """
        for name, args in (('notes:edit', (self.note.slug, )),
                           ('notes:add', None)):
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
