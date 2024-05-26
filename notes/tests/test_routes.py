from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Get test data."""
        cls.author = User.objects.create_user(
            'user1', 'username@mail.com', 'userpasword12')
        cls.another = User.objects.create_user(
            'user2', 'user@mail.ru', 'userpassword2'
        )
        cls.note = Note.objects.create(
            title='название',
            text='текст записи',
            author=cls.author,
            slug='slug'
        )

    def test_pages_avaibility(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),

        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_reqad_edit_and_delete(self):
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug)
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name=name):
                if slug is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=[slug])
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_success_page_for_autentificated_user(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
