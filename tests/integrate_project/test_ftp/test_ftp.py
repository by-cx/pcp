from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from djangosanetesting.cases import DatabaseTestCase, HttpTestCase

class TestFtp(DatabaseTestCase):

    def setUp(self):
        super(TestFtp, self).setUp()


    def test_foo(self):
        pass


class TestFtpRequests(HttpTestCase):


    def setUp(self):
        super(TestFtpRequests, self).setUp()
        call_command('loaddata', settings.USERS_FIXTURE)

        self.user = 'customer'
        self.password = 'vanyli'

    def test_response_redirect_login(self):
        response = self.client.get(reverse('ftp_list'), follow=True)

        self.assert_equals(response.status_code, 200, "FTP list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page")


    def test_list_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('ftp_list'), follow=True)
        self.assert_equals(response.status_code, 200, "FTP list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('ftp_list'), "Logged user should get ftp list, got %s instead" % response.request['PATH_INFO'])

    def test_add_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('ftp_upsert'), follow=True)
        self.assert_equals(response.status_code, 200, "FTP add return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('ftp_upsert'), "Logged user should get ftp form, got %s instead" % response.request['PATH_INFO'])
