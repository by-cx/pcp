# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Machine'
        db.create_table('clients_machine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ipv6', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('clients', ['Machine'])

        # Adding model 'Address'
        db.create_table('clients_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('residency_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('residency_street', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('residency_city', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('residency_city_num', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('residency_ic', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('residency_dic', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('residency_email', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('residency_phone', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('different', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invoice_name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_street', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_city', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_city_num', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
            ('invoice_email', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('invoice_phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('clients', ['Address'])

        # Adding model 'Parms'
        db.create_table('clients_parms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('home', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('uid', self.gf('django.db.models.fields.IntegerField')()),
            ('gid', self.gf('django.db.models.fields.IntegerField')()),
            ('discount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fee', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='czk', max_length=20)),
            ('enable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('address', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['clients.Address'], unique=True)),
            ('web_machine', self.gf('django.db.models.fields.related.ForeignKey')(related_name='web', to=orm['clients.Machine'])),
            ('mail_machine', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mail', to=orm['clients.Machine'])),
            ('mysql_machine', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mysql', to=orm['clients.Machine'])),
            ('pgsql_machine', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pgsql', to=orm['clients.Machine'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('clients', ['Parms'])


    def backwards(self, orm):
        
        # Deleting model 'Machine'
        db.delete_table('clients_machine')

        # Deleting model 'Address'
        db.delete_table('clients_address')

        # Deleting model 'Parms'
        db.delete_table('clients_parms')


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
        'clients.address': {
            'Meta': {'object_name': 'Address'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'different': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'invoice_city_num': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'invoice_email': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'invoice_street': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'residency_city': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'residency_city_num': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'residency_dic': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'residency_email': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'residency_ic': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'residency_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'residency_phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'residency_street': ('django.db.models.fields.CharField', [], {'max_length': '250'})
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
            'address': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['clients.Address']", 'unique': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'czk'", 'max_length': '20'}),
            'discount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fee': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gid': ('django.db.models.fields.IntegerField', [], {}),
            'home': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
