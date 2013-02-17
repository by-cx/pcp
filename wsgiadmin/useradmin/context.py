from django.contrib.sites.models import Site

def rosti_context(request):
    return {
            "site": Site.objects.get_current(),
            }
