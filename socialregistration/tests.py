from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from oauth2 import Client
from socialregistration.signals import login, connect
import mock
import urllib
import urlparse
import re

class TemplateTagTest(object):
    def get_tag(self):
        """
        Return the appropriate {% load %} and {% button %} tag to try rendering
        as a tuple:
        
                ('facebook', 'facebook_button')

        """
        raise NotImplementedError
    
    def test_tag_renders_correctly(self):
        load, button = self.get_tag()

        tpl = """{%% load %s %%}{%% %s %%}""" % (load, button)
        
        self.assertTrue('form' in template.Template(tpl).render(template.Context({'request': None})))
        
        tpl = """{%% load %s %%}{%% %s STATIC_URL 'custom/button/url.jpg' %%}""" % (load, button)
        
        rendered = template.Template(tpl).render(template.Context({
                    'request': None,
                    'STATIC_URL': '/static/'}))

        self.assertTrue('custom/button/url.jpg' in rendered)
        self.assertTrue('/static/' in rendered)


def get_mock_func(func):
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped


class OAuthTest(object):
    """
    Mixin for OAuth tests. This does not go out to the services that we're 
    testing but mocks instead the responses we *should* get back.
    """
    
    # The profile model to be used
    profile = None
    
    def get_redirect_url(self):
        raise NotImplementedError
    
    def get_callback_url(self):
        raise NotImplementedError
    
    def get_callback_setup_url(self):
        raise NotImplementedError
    
    def get_redirect_mock_response(self, *args, **kwargs):
        """
        If the redirect view does any requests, this is the method that returns
        the mocked response. In case of OAuth1 this will be the request token
        response.
        """
        raise NotImplementedError
    
    def get_callback_mock_response(self, *args, **kwargs):
        """
        If the callback view does any request, this is the method that returns
        the mocked response. In case of OAuth{1,2} this will be the access token.
        """
        raise NotImplementedError
    
    def get_setup_callback_mock_response(self, *args, **kwargs):
        """
        If the setup callback view does any requests, this is the method that
        returns the mocked response. In case of OAuth{1,2} this will be the 
        user information that we'll be authenticating with.
        """
        raise NotImplementedError
    
    def create_profile(self, user):
        raise NotImplementedError
    
    def create_user(self, is_active=True):
        user = User.objects.create(username='alen')
        user.set_password('test')
        user.is_active = is_active
        user.save()
        return user
    
    def login(self):
        self.client.login(username='alen', password='test')
        
    def get_counter(self):
        return type('Counter', (object,), {'counter' : 0})()
        
    @mock.patch('oauth2.Client.request')
    def redirect(self, MockRequest):
        MockRequest.side_effect = get_mock_func(self.get_redirect_mock_response)
        response = self.client.post(self.get_redirect_url())
        return response
    
    @mock.patch('oauth2.Client.request')
    def callback(self, MockRequest):
        MockRequest.side_effect = get_mock_func(self.get_callback_mock_response)
        response = self.client.get(self.get_callback_url(), {'oauth_verifier': 'abc'})
        return response
    
    @mock.patch('oauth2.Client.request')
    def setup_callback(self, MockRequest):
        MockRequest.side_effect = get_mock_func(self.get_setup_callback_mock_response)
        response = self.client.get(self.get_setup_callback_url())
        return response
    
    def flow(self):
        self.redirect()
        self.callback()
        return self.setup_callback()
    
    def test_redirect_should_redirect_a_user(self,):
        response = self.redirect()
        self.assertEqual(302, response.status_code, response.content)        
    
    def test_callback_should_redirect_a_user(self):
        self.redirect()
        response = self.callback()
        self.assertEqual(302, response.status_code, response.content)

    def test_setup_callback_should_redirect_a_new_user(self):
        self.redirect()
        self.callback()
        response = self.setup_callback()
        self.assertEqual(302, response.status_code, response.content)
        self.assertEqual(urlparse.urlparse(response['Location']).path, reverse('socialregistration:setup'))
    
    def test_setup_callback_should_redirect_a_logged_in_user(self):
        self.create_user()
        self.login()
        
        self.redirect()
        self.callback()
        response = self.setup_callback()
        self.assertEqual(302, response.status_code, response.content)
        self.assertNotEqual(urlparse.urlparse(response['Location']).path, reverse('socialregistration:setup'))

    def test_connected_user_should_be_logged_in(self):
        user = self.create_user()
        
        self.assertFalse(self.client.session.get('_auth_user_id', False))
        
        self.create_profile(user)

        self.flow()
        
        self.assertEqual(1, self.client.session['_auth_user_id'])
    
    def test_logged_in_user_should_be_connected(self):
        user = self.create_user()
        self.login()
        
        self.assertEqual(0, self.profile.objects.filter(user=user).count())
        
        self.flow()
        
        self.assertEqual(1, self.profile.objects.filter(user=user).count())
    
    def test_only_one_user_can_connect_with_a_provider(self):
        user = self.create_user()
        self.create_profile(user)
        
        other = User.objects.create(username='other')
        other.is_active = True 
        other.set_password('test')
        other.save()
        
        self.client.login(username='other', password='test')
        
        response = self.flow()
        
        self.assertEqual(200, response.status_code, response.content)
        self.assertContains(response, 'This profile is already connected to another user account')
        
    
    def test_logging_in_should_send_the_login_signal(self):
        counter = self.get_counter()
        
        user = self.create_user()
        self.create_profile(user)
        
        def handler(sender, **kwargs):
            counter.counter += 1
            self.assertEqual(self.profile, sender)
            
        login.connect(handler, sender=self.profile, dispatch_uid='socialreg.test.login')
        
        self.flow()
        
        self.assertEqual(1, counter.counter)

    def test_connecting_should_send_the_connect_signal(self):
        counter = self.get_counter()
        
        user = self.create_user()
        self.login()
        
        def handler(sender, **kwargs):
            counter.counter += 1
            self.assertEqual(self.profile, sender)
        
        connect.connect(handler, sender=self.profile, dispatch_uid='socialreg.test.connect')
        
        self.flow()
        
        self.assertEqual(1, counter.counter)
    
    def test_setup_callback_should_indicate_an_inactive_user(self):
        user = self.create_user(is_active=False)
        self.create_profile(user)

        self.redirect()
        self.callback()
        response = self.setup_callback()

        self.assertEqual(200, response.status_code, response.content)
        self.assertContains(response, "inactive", 1)

    def test_setup_callback_should_redirect_an_inactive_user(self):
        settings.LOGIN_INACTIVE_REDIRECT_URL = '/inactive/'

        user = self.create_user(is_active=False)
        self.create_profile(user)

        self.redirect()
        self.callback()
        response = self.setup_callback()

        self.assertEqual(302, response.status_code, response.content)
        self.assertTrue('/inactive/' in response['Location'])

        settings.LOGIN_INACTIVE_REDIRECT_URL = False

class OAuth2Test(OAuthTest):

    def redirect(self):
        response = self.client.post(self.get_redirect_url())
        self._state = re.findall('state=([\w\d]+)&', response['Location'])[0]
        return response
    
    @mock.patch('socialregistration.clients.oauth.OAuth2.request')
    def callback(self, MockRequest):
        MockRequest.side_effect = get_mock_func(self.get_callback_mock_response)
        response = self.client.get(self.get_callback_url(), {'code': 'abc', 'state': self._state})
        return response
    
    @mock.patch('socialregistration.clients.oauth.OAuth2.request')
    def setup_callback(self, MockRequest):
        MockRequest.side_effect = get_mock_func(self.get_setup_callback_mock_response)
        response = self.client.get(self.get_setup_callback_url())
        return response

    def test_state_is_invalid(self):
        self.redirect()
        response = self.client.get(self.get_callback_url(), {'code': 'abc', 'state': "aaaa"})
        self.assertContains(response, "State parameter missing or incorrect")

    def test_state_is_missing(self):
        self.redirect()
        response = self.client.get(self.get_callback_url(), {'code': 'abc'})
        self.assertContains(response, "State parameter missing or incorrect")

    def test_passing_state_check(self):
        self.redirect()
        self.callback()
        response = self.client.get(self.get_callback_url())
        self.assertNotContains(response, "State parameter missing or incorrect",302)


class TestContextProcessors(TestCase):
    def test_request_is_in_context(self):
        self.assertTrue('django.core.context_processors.request' in settings.TEMPLATE_CONTEXT_PROCESSORS)

