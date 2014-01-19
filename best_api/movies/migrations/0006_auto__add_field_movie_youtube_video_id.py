# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Movie.youtube_video_id'
        db.add_column(u'movies_movie', 'youtube_video_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Movie.youtube_video_id'
        db.delete_column(u'movies_movie', 'youtube_video_id')


    models = {
        u'movies.movie': {
            'Meta': {'object_name': 'Movie'},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'imdb_rating': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'plot': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
            'runtime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'youtube_video_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        }
    }

    complete_apps = ['movies']