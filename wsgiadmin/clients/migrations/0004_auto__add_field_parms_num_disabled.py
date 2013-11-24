# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Parms.num_disabled'
        db.add_column(u'clients_parms', 'num_disabled',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Parms.num_disabled'
        db.delete_column(u'clients_parms', 'num_disabled')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'clients.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'vat_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'clients.machine': {
            'Meta': {'object_name': 'Machine'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ipv6': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'clients.parms': {
            'Meta': {'object_name': 'Parms'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'CZK'", 'max_length': '20'}),
            'discount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fee': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gid': ('django.db.models.fields.IntegerField', [], {}),
            'guard_enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'home': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_notification': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'low_level_credits': ('django.db.models.fields.CharField', [], {'default': "'send_email'", 'max_length': '30'}),
            'mail_machine': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'mail'", 'null': 'True', 'blank': 'True', 'to': u"orm['clients.Machine']"}),
            'mysql_machine': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'mysql'", 'null': 'True', 'blank': 'True', 'to': u"orm['clients.Machine']"}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'num_disabled': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_reminds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pgsql_machine': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'pgsql'", 'null': 'True', 'blank': 'True', 'to': u"orm['clients.Machine']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'web_machine': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'web'", 'null': 'True', 'blank': 'True', 'to': u"orm['clients.Machine']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['clients']