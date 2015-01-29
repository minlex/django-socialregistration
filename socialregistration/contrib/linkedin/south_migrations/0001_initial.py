# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LinkedInProfile'
        db.create_table('linkedin_linkedinprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('linkedin_id', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('linkedin', ['LinkedInProfile'])

        # Adding model 'LinkedInRequestToken'
        db.create_table('linkedin_linkedinrequesttoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='request_token', unique=True, to=orm['linkedin.LinkedInProfile'])),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('linkedin', ['LinkedInRequestToken'])

        # Adding model 'LinkedInAccessToken'
        db.create_table('linkedin_linkedinaccesstoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='access_token', unique=True, to=orm['linkedin.LinkedInProfile'])),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('linkedin', ['LinkedInAccessToken'])


    def backwards(self, orm):
        
        # Deleting model 'LinkedInProfile'
        db.delete_table('linkedin_linkedinprofile')

        # Deleting model 'LinkedInRequestToken'
        db.delete_table('linkedin_linkedinrequesttoken')

        # Deleting model 'LinkedInAccessToken'
        db.delete_table('linkedin_linkedinaccesstoken')


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
        'linkedin.linkedinaccesstoken': {
            'Meta': {'object_name': 'LinkedInAccessToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'access_token'", 'unique': 'True', 'to': "orm['linkedin.LinkedInProfile']"})
        },
        'linkedin.linkedinprofile': {
            'Meta': {'object_name': 'LinkedInProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linkedin_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'linkedin.linkedinrequesttoken': {
            'Meta': {'object_name': 'LinkedInRequestToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'request_token'", 'unique': 'True', 'to': "orm['linkedin.LinkedInProfile']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['linkedin']
