import os,sys
from wsgiadmin.bills.tools import create_invoices

sys.path.append('/home/cx/co/pcp')
sys.path.append('/home/cx/co/pcp/wsgiadmin')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wsgiadmin.settings'

create_invoices(False,0)
