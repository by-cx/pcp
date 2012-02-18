from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from djangosanetesting.cases import DatabaseTestCase, HttpTestCase

class TestCron(DatabaseTestCase):

    def setUp(self):
        super(TestCron, self).setUp()


    def test_foo(self):
        pass


class TestCronRequests(HttpTestCase):


    def setUp(self):
        super(TestCronRequests, self).setUp()
        call_command('loaddata', settings.USERS_FIXTURE)

        self.user = 'customer'
        self.password = 'vanyli'

    def test_response_redirect_login(self):
        response = self.client.get(reverse('cron_list'), follow=True)

        self.assert_equals(response.status_code, 200, "Cron list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page")


    def test_list_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('cron_list'), follow=True)
        self.assert_equals(response.status_code, 200, "Cron list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('cron_list'), "Logged user should get Cron list, got %s instead" % response.request['PATH_INFO'])

    def test_add_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('create_cron'), follow=True)
        self.assert_equals(response.status_code, 200, "Cron add return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('create_cron'), "Logged user should get Cron list, got %s instead" % response.request['PATH_INFO'])

