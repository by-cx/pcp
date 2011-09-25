from django.conf import settings
from django.core.urlresolvers import reverse
from djangosanetesting.cases import DatabaseTestCase, HttpTestCase

class TestDomains(DatabaseTestCase):

    def setUp(self):
        super(TestDomains, self).setUp()


    def test_foo(self):
        pass



class TestDomainsRequests(HttpTestCase):

    def test_response(self):
        response = self.client.get(reverse('domains_list'), follow=True)

        self.assert_equals(response.status_code, 200, "Domains list return unexpected code %s" % response.status_code)
        self.assert_equals(response.request['PATH_INFO'], settings.LOGIN_URL, "Anonymous user should be redirected to login page")

