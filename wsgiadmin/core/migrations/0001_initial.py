# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Capability'
        db.create_table(u'core_capability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'core', ['Capability'])

        # Adding model 'Server'
        db.create_table(u'core_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ip', self.gf('django.db.models.fields.CharField')(default='127.0.0.1', max_length=64, null=True, blank=True)),
            ('ipv6', self.gf('django.db.models.fields.CharField')(default='::1', max_length=64, null=True, blank=True)),
            ('ssh_port', self.gf('django.db.models.fields.IntegerField')(default=22)),
            ('os', self.gf('django.db.models.fields.CharField')(default='debian6', max_length=64)),
            ('key', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Server'])

        # Adding M2M table for field capabilities on 'Server'
        m2m_table_name = db.shorten_name(u'core_server_capabilities')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('server', models.ForeignKey(orm[u'core.server'], null=False)),
            ('capability', models.ForeignKey(orm[u'core.capability'], null=False))
        ))
        db.create_unique(m2m_table_name, ['server_id', 'capability_id'])

        # Adding model 'Log'
        db.create_table(u'core_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'core', ['Log'])

        # Adding model 'CommandLog'
        db.create_table(u'core_commandlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Server'])),
            ('command', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('execute_user', self.gf('django.db.models.fields.CharField')(default='root', max_length=128)),
            ('stdin', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rm_stdin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('result_stdout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('result_stderr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status_code', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['CommandLog'])


    def backwards(self, orm):
        # Deleting model 'Capability'
        db.delete_table(u'core_capability')

        # Deleting model 'Server'
        db.delete_table(u'core_server')

        # Removing M2M table for field capabilities on 'Server'
        db.delete_table(db.shorten_name(u'core_server_capabilities'))

        # Deleting model 'Log'
        db.delete_table(u'core_log')

        # Deleting model 'CommandLog'
        db.delete_table(u'core_commandlog')


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
        u'core.capability': {
            'Meta': {'object_name': 'Capability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'core.commandlog': {
            'Meta': {'object_name': 'CommandLog'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'execute_user': ('django.db.models.fields.CharField', [], {'default': "'root'", 'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'result_stderr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'result_stdout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rm_stdin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Server']"}),
            'status_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'stdin': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.log': {
            'Meta': {'object_name': 'Log'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'core.server': {
            'Meta': {'object_name': 'Server'},
            'capabilities': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Capability']", 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'default': "'127.0.0.1'", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'ipv6': ('django.db.models.fields.CharField', [], {'default': "'::1'", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "'debian6'", 'max_length': '64'}),
            'ssh_port': ('django.db.models.fields.IntegerField', [], {'default': '22'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']