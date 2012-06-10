from jsonrpc.proxy import ServiceProxy
from django.conf import settings

s = ServiceProxy(settings.JSONRPC_URL)

#def list_addresses(request):
#def add_address(request,
#def update_address(request,
#def get_address(request, internal_id):
#def add_invoice(request, address_id, items):
#def list_invoices(request):

#TODO:What with connection error? Queue?

def test():
    print s.hello(settings.JSONRPC_USERNAME, settings.JSONRPC_PASSWORD)

def address():
    print s.list_addresses(settings.JSONRPC_USERNAME, settings.JSONRPC_PASSWORD)