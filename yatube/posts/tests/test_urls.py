from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_not_author = User.objects.create_user(username='NotAuthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_not_author)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        cache.clear()

    def test_200_not_auth(self):
        """Проверка доступности страниц."""
        urls = ((reverse('posts:index')),
                (reverse('posts:profile', args={'auth'})),
                (reverse('posts:post_detail', args={'1'})),
                (reverse('posts:group_list', args={'test-slug'}))
                )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_200_auth(self):
        """Проверка доступности страниц."""
        urls = ((reverse('posts:index')),
                (reverse('posts:profile', args={'auth'})),
                (reverse('posts:post_detail', args={'1'})),
                (reverse('posts:group_list', args={'test-slug'})),
                (reverse('posts:post_create')),
                )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_200_auth_author(self):
        """Проверка доступности страниц."""
        urls = ((reverse('posts:index')),
                (reverse('posts:profile', args={'auth'})),
                (reverse('posts:post_detail', args={'1'})),
                (reverse('posts:group_list', args={'test-slug'})),
                (reverse('posts:post_create')),
                (reverse('posts:post_edit', args={'1'})),
                )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, 200)

    def test_404_not_auth(self):
        """Проверка вывода ошибки 404 для несуществующего адреса."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_404_auth(self):
        """Проверка вывода ошибки 404 для несуществующего адреса."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_correct_template_not_auth(self):
        """URL-адрес использует соответствующий шаблон."""
        address_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
        }
        for key, value in address_templates.items():
            with self.subTest(key=key):
                response = self.guest_client.get(key)
                self.assertTemplateUsed(response, value)

    def test_correct_template_auth(self):
        """URL-адрес использует соответствующий шаблон."""
        address_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for key, value in address_templates.items():
            with self.subTest(key=key):
                response = self.authorized_client.get(key)
                self.assertTemplateUsed(response, value)

    def test_correct_template_author(self):
        """URL-адрес использует соответствующий шаблон."""
        address_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
        }
        for key, value in address_templates.items():
            with self.subTest(key=key):
                response = self.authorized_client_author.get(key)
                self.assertTemplateUsed(response, value)

    def test_302_not_auth_for_create_and_edit(self):
        """Страница по адресу /create/ и /edit/ перенаправит анонимного
        пользователя на страницу логина."""
        cut_to_login = reverse('users:login')
        cut_to_post_create = reverse('posts:post_create')
        cut_to_post_edit = reverse('posts:post_edit', kwargs={'post_id': '1'})
        address_redirect = {
            cut_to_post_create:
            f'{cut_to_login}?next={cut_to_post_create}',
            cut_to_post_edit:
            f'{cut_to_login}?next={cut_to_post_edit}',
        }
        for key, value in address_redirect.items():
            with self.subTest(key=key):
                response = self.guest_client.get(key, follow=True)
                self.assertRedirects(response, value)

    def test_302_auth_not_author(self):
        """Страница по адресу /edit/ перенаправит не автора поста
        на страницу поста."""
        response = (self.authorized_client.get(reverse('posts:post_edit',
                    kwargs={'post_id': '1'}), follow=True))
        self.assertRedirects(response, (reverse('posts:post_detail',
                             kwargs={'post_id': '1'})))

    def test_302_not_auth_for_add_comment(self):
        """Страница по адресу /comment/ перенаправит анонимного
        пользователя на страницу входа."""
        cut_to_login = reverse('users:login')
        cut_to_add_comment = reverse('posts:add_comment',
                                     kwargs={'post_id': '1'})
        response = self.guest_client.get(cut_to_add_comment, follow=True)
        self.assertRedirects(response,
                             (f'{cut_to_login}?next={cut_to_add_comment}'))
