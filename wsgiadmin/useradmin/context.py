from django.conf import settings
from django.contrib.sites.models import Site

def rosti_context(request):
    return {"SERVER_NAME": settings.SERVER_NAME,
            "WIKI_URL": settings.WIKI_URL,
            "CONTRACT_URL": settings.CONTRACT_URL,
            "site": Site.objects.get_current(),
            }
