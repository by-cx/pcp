# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Address'
        db.delete_table('clients_address')

        # Deleting field 'Parms.address'
        db.delete_column('clients_parms', 'address_id')


    def backwards(self, orm):
        
        # Adding model 'Address'
        db.create_table('clients_address', (
            ('residency_city_num', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('different', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('residency_street', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('residency_phone', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('residency_dic', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('residency_ic', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('invoice_phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('residency_email', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('invoice_city_num', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
            ('invoice_city', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('residency_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_email', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('residency_city', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice_street', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
        ))
        db.send_create_signal('clients', ['Address'])

        # User chose to not deal with backwards NULL issues for 'Parms.address'
        raise RuntimeError("Cannot reverse this migration. 'Parms.address' and its values cannot be restored.")


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
        'clients.machine': {
            'Meta': {'object_name': 'Machine'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ipv6': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'clients.parms': {
            'Meta': {'object_name': 'Parms'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'czk'", 'max_length': '20'}),
            'discount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fee': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gid': ('django.db.models.fields.IntegerField', [], {}),
            'home': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_notification': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'low_level_credits': ('django.db.models.fields.CharField', [], {'default': "'send_email'", 'max_length': '30'}),
            'mail_machine': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mail'", 'to': "orm['clients.Machine']"}),
            'mysql_machine': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mysql'", 'to': "orm['clients.Machine']"}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pgsql_machine': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pgsql'", 'to': "orm['clients.Machine']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'web_machine': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'web'", 'to': "orm['clients.Machine']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['clients']
