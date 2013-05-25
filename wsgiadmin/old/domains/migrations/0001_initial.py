# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Domain'
        db.create_table(u'domains_domain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('dns', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mail', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ipv4', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ipv6', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subdomains', null=True, to=orm['domains.Domain'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'domains', ['Domain'])

        # Adding unique constraint on 'Domain', fields ['name', 'parent']
        db.create_unique(u'domains_domain', ['name', 'parent_id'])

        # Adding model 'RegistrationRequest'
        db.create_table(u'domains_registrationrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('passwd', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('years', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'domains', ['RegistrationRequest'])


    def backwards(self, orm):
        # Removing unique constraint on 'Domain', fields ['name', 'parent']
        db.delete_unique(u'domains_domain', ['name', 'parent_id'])

        # Deleting model 'Domain'
        db.delete_table(u'domains_domain')

        # Deleting model 'RegistrationRequest'
        db.delete_table(u'domains_registrationrequest')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'domains.domain': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Domain'},
            'dns': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subdomains'", 'null': 'True', 'to': u"orm['domains.Domain']"}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'domains.registrationrequest': {
            'Meta': {'object_name': 'RegistrationRequest'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'passwd': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'years': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['domains']