# -*- coding: utf-8 -*-

import datetime
from wsgiadmin.keystore.models import store

def kget(key, default=None):
    """
    Vrací hodnotu uloženou pod klíčem a nebo default
    """

    try:
        ik = store.objects.get(key=key)
        ik.date_read = datetime.datetime.today()
        ik.save()
        return ik.value
    except store.DoesNotExist:
        return default


def kset(key, value, expire=0):
    """
    Nastavuje hodnotu pod klíč
    """
    try:
        ik = store.objects.get(key=key)
        ik.date_write = datetime.datetime.today()
    except store.DoesNotExist:
        ik = store(key=key)

    ik.value = value
    ik.expire = expire
    ik.save()

    return True


def krm(key):
    """
    Smaže klíč
     """
    try:
        store.objects.get(key=key).delete()
    except store.DoesNotExist:
        return False
    else:
        return True

def klist():
    """
     List uložených klíčů
    """
    return [x.key for x in store.objects.all()]
