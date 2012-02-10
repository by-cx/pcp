# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
import logging
logger = logging.getLogger(__name__)


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SiteDomain'
        db.create_table('apacheconf_sitedomain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['domains.Domain'])),
            ('user_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['apacheconf.UserSite'])),
        ))
        db.send_create_signal('apacheconf', ['SiteDomain'])

        # Adding field 'UserSite.main_domain'
        db.add_column('apacheconf_site', 'main_domain', self.gf('django.db.models.fields.related.ForeignKey')(related_name='main_domain', null=True, to=orm['domains.Domain']), keep_default=False)

        if not db.dry_run:
            for one in orm.UserSite.objects.all():
                domains = one.domains.split()
                try:
                    one.main_domain = orm.Domain.objects.get(name=domains[0].strip(), owner=one.owner)
                except orm.Domain.DoesNotExist:
                    logger.error("0004 migration: site %s - MAIN domain %s not found, owner %s" % (one.pk, domains[0], one.owner.username))

                if len(domains) > 1:
                    for two in domains[1:]:
                        try:
                            one.misc_domains.add(orm.Domain.objects.get(name=two.strip(), owner=one.owner))
                        except orm.Domain.DoesNotExist:
                            logger.error("0004 migration: site %s - misc domain %s not found, owner %s" % (one.pk, domains[0], one.owner.username))

    def backwards(self, orm):
        
        # Deleting model 'SiteDomain'
        db.delete_table('apacheconf_sitedomain')

        # Deleting field 'UserSite.main_domain'
        db.delete_column('apacheconf_site', 'main_domain_id')


    models = {
        'apacheconf.sitedomain': {
            'Meta': {'object_name': 'SiteDomain'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domains.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['apacheconf.UserSite']"})
        },
        'apacheconf.usersite': {
            'Meta': {'object_name': 'UserSite', 'db_table': "'apacheconf_site'"},
            'allow_ips': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deny_ips': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'document_root': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'domains': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'htaccess': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indexes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'main_domain': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'main_domain'", 'null': 'True', 'to': "orm['domains.Domain']"}),
            'misc_domains': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'misc_domains'", 'null': 'True', 'through': "orm['apacheconf.SiteDomain']", 'to': "orm['domains.Domain']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'processes': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'python_path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ssl_crt': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'ssl_key': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'ssl_mode': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'static': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'threads': ('django.db.models.fields.IntegerField', [], {'default': '5', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'virtualenv': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '100', 'blank': 'True'})
        },
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
        'domains.domain': {
            'Meta': {'object_name': 'Domain'},
            'dns': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['apacheconf']
