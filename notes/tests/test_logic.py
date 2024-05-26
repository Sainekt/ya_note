from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    TEXT = 'text'
    TITLE = 'title'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='username')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.url_add_page = reverse('notes:add')
        cls.succes_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG}

    def test_anonimous_cant_create_note(self):
        self.client.post(self.url_add_page, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_login_user_can_create_note(self):
        response = self.auth_user.post(self.url_add_page, data=self.form_data)
        self.assertRedirects(response, self.succes_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_one_slug_two_try(self):
        response = self.auth_user.post(self.url_add_page, data=self.form_data)
        response = self.auth_user.post(self.url_add_page, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )

    def test_auto_slug_for_note(self):
        self.auth_user.post(self.url_add_page, data={
            'title': self.TITLE,
            'text': self.TEXT
        })
        note = Note.objects.get()
        max_slug_length = Note._meta.get_field('slug').max_length
        note_slug = slugify(note.title)[:max_slug_length]
        self.assertEqual(note.slug, note_slug)


class TestNoteEditDelete(TestCase):

    TEXT = 'text'
    NEW_TEXT = 'new_text'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='username')
        cls.another_user = User.objects.create(username='another_user')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.auth_another = Client()
        cls.auth_another.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title='title',
            text=cls.TEXT,
            author=cls.user)
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_succes = reverse('notes:success')
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.TEXT, 'text': cls.NEW_TEXT}

    def test_author_can_delete_note(self):
        response = self.auth_user.delete(self.url_delete)
        self.assertRedirects(response, self.url_succes)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_another_user_cant_delete_note_of_user(self):
        response = self.auth_another.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_edit_his_note(self):
        response = self.auth_user.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_succes)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TEXT)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.auth_another.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'title')
        self.assertEqual(self.note.text, self.TEXT)
