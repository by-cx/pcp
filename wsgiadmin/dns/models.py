import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DNSException(Exception): pass


RECORD_TYPES = (
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "SRV",
    "TXT",
)


class Domain(models.Model):
    last_modified = models.DateTimeField(_("Update date"), auto_now=True)
    serial = models.IntegerField(_("Serial"), default=0)
    nss = models.CharField(_("Name servers"), max_length=512, help_text=_("Name servers separated by space"), default="ns1.rosti.cz ns2.rosti.cz")
    name = models.CharField(_("Domain"), max_length=256)
    rname = models.EmailField(_("Admin e-mail"))
    ttl = models.IntegerField(_("TTL"), default=86400)
    user = models.ForeignKey(User, related_name="dns_set")

    def new_serial(self):
        today = datetime.date.today()
        if self.serial:
            serial = unicode(self.serial)
            year, month, day, num = int(serial[0:4]), int(serial[4:6]), int(serial[6:8]), int(serial[8:10])
            if (year, month, day) == (today.year, today.month, today.day):
                num += 1
                if num > 99:
                    raise DNSException("Num is too big (%d)" % num)
                self.serial = int("%.4d%.2d%.2d%.2d" % (year, month, day, num))
                self.save()
                return
        self.serial = int("%.4d%.2d%.2d%.2d" % (today.year, today.month, today.day, 1))
        self.save()


class Record(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    record_type = models.CharField(_("Type"), max_length=32, choices=[(x, x) for x in RECORD_TYPES])
    value = models.CharField(_("Value"), max_length=256)
    ttl = models.IntegerField(_("TTL"), null=True, blank=True)
    order_num = models.IntegerField(_("Order number"))
    prio = models.IntegerField(_("Priority"), blank=True, null=True)
    domain = models.ForeignKey(Domain)

    def up(self):
        records = list(self.domain.record_set.order_by("order_num"))
        try:
            previous = records[records.index(self) - 1]
            my_order_num, prev_order_num = self.order_num, previous.order_num
            previous.order_num = my_order_num
            previous.save()
            self.order_num = prev_order_num
            self.save()
        except IndexError:
            pass

    def down(self):
        records = list(self.domain.record_set.order_by("order_num"))
        try:
            next = records[records.index(self) + 1]
            my_order_num, next_order_num = self.order_num, next.order_num
            next.order_num = my_order_num
            next.save()
            self.order_num = next_order_num
            self.save()
        except IndexError:
            pass

    def save(self, *args, **kwargs):
        if not self.order_num and self.domain.record_set.count():
            self.order_num = max([x.order_num for x in self.domain.record_set.all()]) + 1
        #TODO: consider of happines from this code
        #elif Record.objects.filter(order_num=self.order_num) and Record.objects.get(order_num=self.order_num) != self:
        #    self.order_num = Record.objects.get(order_num=self.order_num).order_num
        #    for record in Record.objects.filter(order_num=self.order_num).order_by("order_num").reverse():
        #        record.order_num += 1
        #        record.save()
        else:
            self.order_num = 1
        self.domain.save()
        super(Record, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s record for domain %s named %s with value %s" % (self.record_type, self.domain.name, self.name, self.value)
