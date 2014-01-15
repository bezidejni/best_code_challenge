# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Movie.imdb_rating'
        db.add_column(u'movies_movie', 'imdb_rating',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=3, blank=True),
                      keep_default=False)

        # Adding field 'Movie.imdb_id'
        db.add_column(u'movies_movie', 'imdb_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=15, blank=True),
                      keep_default=False)

        # Adding field 'Movie.runtime'
        db.add_column(u'movies_movie', 'runtime',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Movie.plot'
        db.add_column(u'movies_movie', 'plot',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Movie.imdb_rating'
        db.delete_column(u'movies_movie', 'imdb_rating')

        # Deleting field 'Movie.imdb_id'
        db.delete_column(u'movies_movie', 'imdb_id')

        # Deleting field 'Movie.runtime'
        db.delete_column(u'movies_movie', 'runtime')

        # Deleting field 'Movie.plot'
        db.delete_column(u'movies_movie', 'plot')


    models = {
        u'movies.movie': {
            'Meta': {'object_name': 'Movie'},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'imdb_rating': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'plot': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'runtime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['movies']