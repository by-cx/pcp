# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteDomain'
        db.create_table(u'apacheconf_sitedomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['domains.Domain'])),
            ('user_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apacheconf.UserSite'])),
        ))
        db.send_create_signal(u'apacheconf', ['SiteDomain'])

        # Adding model 'UserSite'
        db.create_table('apacheconf_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('main_domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='main_domain', null=True, to=orm['domains.Domain'])),
            ('document_root', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('htaccess', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('indexes', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_ips', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('deny_ips', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('script', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('processes', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('threads', self.gf('django.db.models.fields.IntegerField')(default=5, blank=True)),
            ('virtualenv', self.gf('django.db.models.fields.CharField')(default='default', max_length=100, blank=True)),
            ('static', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('python_path', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('extra', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ssl_crt', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('ssl_key', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('ssl_mode', self.gf('django.db.models.fields.CharField')(default='none', max_length=20)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'apacheconf', ['UserSite'])


    def backwards(self, orm):
        # Deleting model 'SiteDomain'
        db.delete_table(u'apacheconf_sitedomain')

        # Deleting model 'UserSite'
        db.delete_table('apacheconf_site')


    models = {
        u'apacheconf.sitedomain': {
            'Meta': {'object_name': 'SiteDomain'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['domains.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['apacheconf.UserSite']"})
        },
        u'apacheconf.usersite': {
            'Meta': {'object_name': 'UserSite', 'db_table': "'apacheconf_site'"},
            'allow_ips': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deny_ips': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'document_root': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'htaccess': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indexes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'main_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'main_domain'", 'null': 'True', 'to': u"orm['domains.Domain']"}),
            'misc_domains': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'misc_domains'", 'to': u"orm['domains.Domain']", 'through': u"orm['apacheconf.SiteDomain']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'processes': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'python_path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ssl_crt': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'ssl_key': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'ssl_mode': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'static': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'threads': ('django.db.models.fields.IntegerField', [], {'default': '5', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'virtualenv': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '100', 'blank': 'True'})
        },
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
        }
    }

    complete_apps = ['apacheconf']