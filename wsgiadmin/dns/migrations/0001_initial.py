# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Domain'
        db.create_table('dns_domain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('nss', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('rname', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=86400)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dns_set', to=orm['auth.User'])),
        ))
        db.send_create_signal('dns', ['Domain'])

        # Adding model 'Record'
        db.create_table('dns_record', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('record_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('prio', self.gf('django.db.models.fields.IntegerField')()),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.Domain'])),
        ))
        db.send_create_signal('dns', ['Record'])


    def backwards(self, orm):
        # Deleting model 'Domain'
        db.delete_table('dns_domain')

        # Deleting model 'Record'
        db.delete_table('dns_record')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'nss': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'rname': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '86400'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dns_set'", 'to': "orm['auth.User']"})
        },
        'dns.record': {
            'Meta': {'object_name': 'Record'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dns.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'prio': ('django.db.models.fields.IntegerField', [], {}),
            'record_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['dns']