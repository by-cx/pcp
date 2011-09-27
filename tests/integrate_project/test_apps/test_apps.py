from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from djangosanetesting.cases import HttpTestCase



class TestAppRequests(HttpTestCase):


    def setUp(self):
        super(TestAppRequests, self).setUp()
        call_command('loaddata', settings.USERS_FIXTURE)

        self.user = 'customer'
        self.password = 'vanyli'

    def test_response_redirect_login(self):
        response = self.client.get(reverse('app_list'), follow=True)

        self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page")


    def test_response_ok(self):
        logged = self.client.login(username=self.user, password=self.password)
        self.assert_equals(logged, True, "Login failed")

        response = self.client.get(reverse('app_list'), follow=True)
        self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], reverse('app_list'), "Logged user should get list, got %s instead" % response.request['PATH_INFO'])
