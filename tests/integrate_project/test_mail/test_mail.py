from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from djangosanetesting.cases import DatabaseTestCase, HttpTestCase

class TestMail(DatabaseTestCase):

    def setUp(self):
        super(TestMail, self).setUp()


    def test_foo(self):
        pass


class TestMailRequests(HttpTestCase):


    def setUp(self):
        super(TestMailRequests, self).setUp()
        call_command('loaddata', settings.USERS_FIXTURE)

        self.user = 'customer'
        self.password = 'vanyli'

    def test_response_redirect_login(self):
        response = self.client.get(reverse('mailbox_list'), follow=True)

        self.assert_equals(response.status_code, 200, "Mail list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page")


    def test_list_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('mailbox_list'), follow=True)
        self.assert_equals(response.status_code, 200, "Mail list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('mailbox_list'), "Logged user should get Mail list, got %s instead" % response.request['PATH_INFO'])

    def test_add_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('add_mailbox'), follow=True)
        self.assert_equals(response.status_code, 200, "Mail add return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('add_mailbox'), "Logged user should get Mail form, got %s instead" % response.request['PATH_INFO'])



    def test_list_alias_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('redirect_list'), follow=True)
        self.assert_equals(response.status_code, 200, "Mail list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('redirect_list'), "Logged user should get Mail list, got %s instead" % response.request['PATH_INFO'])

    def test_add_alias_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('add_redirect'), follow=True)
        self.assert_equals(response.status_code, 200, "Mail add return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('add_redirect'), "Logged user should get Mail form, got %s instead" % response.request['PATH_INFO'])
