from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def show(request, t, p=1):
    p = int(p)
    u = request.session.get('switched_user', request.user)
    superuser = request.user

    if t == "income":
        paginator = Paginator(u.income_set.order_by("pub_date").reverse(), 100)
    else:
        paginator = Paginator(u.bill_set.order_by("pub_date").reverse(), 100)

    if not paginator.count:
        page = None
    else:
        page = paginator.page(p)

    return render_to_response("bill.html",
            {
            "items": page,
            "paginator": paginator,
            "type": t,
            "u": u,
            "superuser": superuser,
            "menu_active": "dashboard",
            }, context_instance=RequestContext(request))
