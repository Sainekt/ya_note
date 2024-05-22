from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    LIST_PAGE_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            'user1', 'username@mail.com', 'userpasword12')
        Note.objects.bulk_create(
            Note(
                title=f'Заголовок{index}',
                text='text',
                author=cls.author,
                slug=index)
            for index in range(50))

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_PAGE_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 50)

    def test_Note_orders(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_PAGE_URL)
        object_list = response.context['object_list']
        all_kp = [note.id for note in object_list]
        sorted_pk = sorted(all_kp)
        self.assertEqual(all_kp, sorted_pk)


class TestAddPage(TestCase):

    ADD_PAGE_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            'user1', 'username@mail.com', 'userpasword12')

    def test_form_in_add_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_PAGE_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
