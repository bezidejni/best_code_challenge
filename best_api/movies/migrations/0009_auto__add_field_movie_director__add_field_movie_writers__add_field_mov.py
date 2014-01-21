# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Movie.director'
        db.add_column(u'movies_movie', 'director',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True),
                      keep_default=False)

        # Adding field 'Movie.writers'
        db.add_column(u'movies_movie', 'writers',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Movie.actors'
        db.add_column(u'movies_movie', 'actors',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Movie.director'
        db.delete_column(u'movies_movie', 'director')

        # Deleting field 'Movie.writers'
        db.delete_column(u'movies_movie', 'writers')

        # Deleting field 'Movie.actors'
        db.delete_column(u'movies_movie', 'actors')


    models = {
        u'movies.movie': {
            'Meta': {'ordering': "['title']", 'object_name': 'Movie'},
            'actors': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'director': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'imdb_rating': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'plot': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
            'runtime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'writers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'youtube_video_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        }
    }

    complete_apps = ['movies']