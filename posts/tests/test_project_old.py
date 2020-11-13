from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from posts.models import User, Post, Group

from typing import List


class ProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='johnny')
        self.authorized_client = Client()        
        self.authorized_client.force_login(self.user)
        self.unauthorized_client = Client()
        self.group = Group.objects.create(
            title='first group', 
            slug='first', 
            description='description',
        )       

    def test_authorized_user_profile(self):
        response = self.authorized_client.get(
            reverse('profile', 
            args=(self.user.username,)),
        )
        self.assertEqual(response.status_code, 200)

    def test_authorized_user_newpost(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('new_post'), 
            {'text': 'some text'}, 
            follow=True,
        )       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_unauthorized_user_newpost(self):
        response = self.unauthorized_client.get(
            reverse('new_post'), 
            follow=False,
        )
        self.assertEqual(response.status_code, 302)

    def test_newpost(self):
        Post.objects.create(
            text='some text', 
            author=self.user, 
            group=self.group,
        )
        new_post_id = Post.objects.count()
        key = make_template_fragment_key('index_page')
        cache.touch(key, 0)
        urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,)), 
            reverse('post', args=(self.user.username, new_post_id)),
        ]
        self.url_content_test(urls)

    def test_authorized_user_editpost(self):
        Post.objects.create(
            text='some text', 
            author=self.user, 
            group=self.group,
        )
        new_post_id = Post.objects.count()
        post = Post.objects.get(id=new_post_id)
        post.text = 'here we go again'
        post.save()
        key = make_template_fragment_key('index_page')
        cache.touch(key, 0)
        urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,)), 
            reverse('post', args=(self.user.username, new_post_id)),
            reverse('group_posts', args=(self.group.slug,)),
        ]
        self.url_content_test(urls)
       
    def url_content_test(self, urls: List[str]): 
        for url in urls:
            response = self.authorized_client.get(url) 
            if response.context.get('paginator'):
                post = response.context['page'][0]
            else:
                post = response.context['post']
            with self.subTest():    
                self.assertContains( 
                    response,  
                    post.text,  
                    status_code=200, 
                )  
                self.assertContains( 
                    response,  
                    post.author,  
                    status_code=200, 
                )
                self.assertContains( 
                    response,  
                    post.group,  
                    status_code=200, 
                )
