# -*- coding: utf-8 -*-
import datetime
from constance import config
from django.contrib.auth.models import User
from south.db import db
from south.v2 import DataMigration
from django.db import models
from wsgiadmin.domains.models import Domain

class Migration(DataMigration):

    def default_records(self, orm, domain):
        record = orm['dns.record']()
        record.name = "@"
        record.record_type = "A"
        record.value = config.dns_default_a
        record.ttl = config.dns_default_record_ttl
        record.domain = domain
        record.order_num = 2
        record.save()

        record = orm['dns.record']()
        record.name = "@"
        record.record_type = "AAAA"
        record.value = config.dns_default_aaaa
        record.ttl = config.dns_default_record_ttl
        record.domain = domain
        record.order_num = 3
        record.save()

        record = orm['dns.record']()
        record.name = "@"
        record.record_type = "MX"
        record.value = config.dns_default_mx
        record.ttl = config.dns_default_record_ttl
        record.domain = domain
        record.order_num = 1
        record.save()

        record = orm['dns.record']()
        record.name = "www"
        record.record_type = "CNAME"
        record.value = "@"
        record.ttl = config.dns_default_record_ttl
        record.domain = domain
        record.order_num = 4
        record.save()

    def forwards(self, orm):
        #TODO: this is really ugly and wont work in the future
        for domain in Domain.objects.all():
            if not domain.parent and domain.dns:
                converted_domains = [x.name for x in orm['dns.domain'].objects.all()]
                if domain.name in converted_domains:
                    print "\t\tSkip domain %s (duplicity)" % domain.name
                    continue
                dns = orm['dns.domain']()
                dns.name = domain.name
                dns.rname = "info@rosti.cz"
                dns.user = orm['auth.User'].objects.get(id=domain.owner.id)
                dns.save()
                self.default_records(orm, dns)
                print "\tDomain %s converted to dns" % domain.name

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dns.domain': {
            'Meta': {'object_name': 'Domain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'rname': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '86400'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dns_set'", 'to': "orm['auth.User']"})
        },
        'dns.record': {
            'Meta': {'object_name': 'Record'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'@'", 'max_length': '256'}),
            'order_num': ('django.db.models.fields.IntegerField', [], {}),
            'prio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'record_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['dns']
    symmetrical = True
