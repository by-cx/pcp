import anyjson
from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from djangosanetesting.cases import HttpTestCase, DestructiveDatabaseTestCase
from wsgiadmin.service.views import JsonResponse


class TestUnloggedRequests(HttpTestCase):


    def test_response_redirect_login(self):
        response = self.client.get(reverse('app_list'), follow=True)

        self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page, got %s" % response.request['PATH_INFO'])


class TestAppsRequests(HttpTestCase):

    def setUp(self):
        super(TestAppsRequests, self).setUp()
        call_command('loaddata', settings.USERS_FIXTURE)
        call_command('loaddata', settings.APPS_FIXTURE)

        self.user = 'customer'
        self.password = 'vanyli'


        self.logged_in = self.client.login(username=self.user, password=self.password)

    def test_user_is_logged(self):
        self.assert_equals(self.logged_in, True, "User is not logged in .(")


    def test_get_requests_ok(self):
        urls = (
            reverse('app_list'),

            reverse('app_wsgi'),
            reverse('app_wsgi', kwargs={'app_id': 1}),

            reverse('app_static', kwargs={'app_type': 'static'}),
            reverse('app_static', kwargs={'app_type': 'php'}),
            reverse('app_static', kwargs={'app_type': 'static', 'app_id': 2}),
            reverse('app_static', kwargs={'app_type': 'php', 'app_id': 3}),
        )

        for one in urls:
            response = self.client.get(one, follow=True)
            self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
            self.assert_equals(response.request['PATH_INFO'], one, "Logged user should get URL %s, got %s instead" % (one, response.request['PATH_INFO']))


    def test_post_requests_ok(self):

        #wsgis = get_user_wsgis(request.session.get('switched_user', request.user), False)
        #return JsonResponse('OK', wsgis)

        urls = (
            reverse('refresh_wsgi'),
            reverse('refresh_venv'),
            reverse('refresh_userdirs'),
        )

        for one in urls:
            response = self.client.post(one, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            res_json = anyjson.loads(response.content)
            self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
            self.assert_equals(response.request['PATH_INFO'], one, "User should get URL %s, got %s instead" % (one, response.request['PATH_INFO']))
            self.assert_equals(res_json['result'], "OK", "Did not get `OK` response")

    def test_remove_site_ok(self):

        urls = (
            reverse('remove_site'),
        )

        for one in urls:
            response = self.client.post(one, {'object_id': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            res_json = anyjson.loads(response.content)
            self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
            self.assert_equals(response.request['PATH_INFO'], one, "User should get URL %s, got %s instead" % (one, response.request['PATH_INFO']))
            self.assert_equals(res_json['result'], "OK", "Did not get `OK` response")


    def test_remove_site_forbidden(self):
        """
        try remove app of another user
        """

        urls = (
            reverse('remove_site'),
        )

        for one in urls:
            response = self.client.post(one, {'object_id': 4}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            res_json = anyjson.loads(response.content)
            self.assert_equals(response.status_code, 200, "List return unexpected code %s" % response.status_code)
            self.assert_equals(response.request['PATH_INFO'], one, "Logged user should get URL %s, got %s instead" % (one, response.request['PATH_INFO']))
            self.assert_equals(res_json['result'], "KO", "Did not get `KO` response")
