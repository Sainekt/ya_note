import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture  # создаем автора
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture  # создаем второго пользователя.
def not_author(django_user_model):
    return django_user_model.objects.create(username='не автор')


@pytest.fixture  # логиним автора
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        author=author,
        slug='note-slug',
    )
    return note


@pytest.fixture
def slug_for_args(note):
    return (note.slug,)
