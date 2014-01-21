import cPickle as pickle
import os
from math import sqrt
from statsmodels.tools.eval_measures import meanabs, rmse
from django.core.cache import cache
from django.conf import settings


class ItemBasedRecommender(object):

    def __init__(self, **kwargs):
        defaults = {
            'damp_factor': 25,
            'load_from_disk': False,
            'min_num_of_ratings': 5,
            'model_files_path': settings.BASE_DIR,
            'num_of_results': 20,
            'similar_calculate': 30,
            'similarity_function': 'sim_cosine',
            'training_set_percent': 80,
        }
        self.averages = {}
        self.training_set = {}
        self.test_set = {}
        self.similarity_matrix = {}

        # save parameters from kwargs or use defaults
        for (key, default_val) in defaults.iteritems():
            setattr(self, key, kwargs.get(key, default_val))

        if self.load_from_disk:
            self.load_model()

    def load_model(self):
        training_set = cache.get('training_set')
        if training_set:
            self.training_set = training_set
        else:
            training_data_path = os.path.join(self.model_files_path, 'training_data.p')
            with open(training_data_path, 'rb') as fp:
                data = pickle.load(fp)
            self.training_set = data
            cache.set('training_set', data, 300)
        similarity_matrix = cache.get('similarity_matrix')
        if similarity_matrix:
            self.similarity_matrix = similarity_matrix
        else:
            similarity_matrix_path = os.path.join(self.model_files_path, 'similarity_matrix.p')
            with open(similarity_matrix_path, 'rb') as fp:
                data = pickle.load(fp)
            self.similarity_matrix = data
            cache.set('similarity_matrix', data, 300)

    def save_model_to_disk(self):
        if self.training_set:
            training_data_path = os.path.join(self.model_files_path, 'training_data.p')
            with open(training_data_path, 'wb') as fp:
                pickle.dump(self.training_set, fp)
        if self.similarity_matrix:
            similarity_matrix_path = os.path.join(self.model_files_path, 'similarity_matrix.p')
            with open(similarity_matrix_path, 'wb') as fp:
                pickle.dump(self.similarity_matrix, fp)

    def getRecommendedItems(self, user):
        userRatings = user
        scores = {}
        totalSim = {}
        #itemMatch = transformPrefs(itemMatch)
        # Loop over items rated by this user
        for (item, rating) in userRatings.items():

            # Loop over items similar to this one
            for (similarity, item2) in self.similarity_matrix[item]:

                # Ignore if this user has already rated this item
                if item2 in userRatings:
                    continue
                # Weighted sum of rating times similarity
                scores.setdefault(item2, 0)
                scores[item2] += (similarity * rating)
                # Sum of all the similarities
                totalSim.setdefault(item2, 0)
                totalSim[item2] += similarity
        # Divide each total score by total weighting to get an average, orders them descending by rating
        rankings = [(score, item) for item, score in scores.items()]
        rankings.sort(reverse=True)
        # gets only the movie IDs from the sorted list
        movie_ids = [int(ranking[1]) for ranking in rankings]
        return movie_ids

    def evaluate(self):
        pass

    # Returns the best matches for person from the prefs dictionary.
    # Number of results and similarity function are optional params.
    def topMatches(self, person):
        similarity = getattr(self, self.similarity_function)
        if not self.averages:
            self.calculate_averages()
        scores = [(similarity(person, other), other)
                  for other, ratings in self.training_set.iteritems()
                  if other != person and len(ratings) > self.min_num_of_ratings]
        scores.sort()
        scores.reverse()
        return scores[0:self.num_of_results]

    def calculateSimilarItems(self):
        # Create a dictionary of items showing which other items they
        # are most similar to.
        #prefs = self.transformPrefs()
        # Invert the preference matrix to be item-centric
        #prefs = transformPrefs(prefs)
        c = 0
        for item in self.training_set:
            # Status updates for large datasets
            c += 1
            if c % 100 == 0:
                print "%d / %d" % (c, len(self.training_set))
            # Find the most similar items to this one
            scores = self.topMatches(item)
            self.similarity_matrix[item] = scores
        return self.similarity_matrix

    def calculate_averages(self):
        inverted = self.transformPrefs()
        for user, ratings in inverted.iteritems():
            if not user in self.averages:
                total_ratings = sum([rating for title, rating in ratings.iteritems()])
                total_items = len(ratings)
                self.averages[user] = total_ratings / total_items

    def sim_pearson(self, p1, p2):
        # Returns the Pearson correlation coefficient for p1 and p2
        # Get the list of mutually rated items
        si = {}
        for item in self.training_set[p1]:
            if item in self.training_set[p2]:
                si[item] = 1

        # if they are no ratings in common, return 0
        if len(si) == 0:
            return 0

        # Sum calculations
        n = len(si)

        # Sums of all the preferences
        sum1 = sum([self.training_set[p1][it] for it in si])
        sum2 = sum([self.training_set[p2][it] for it in si])

        # Sums of the squares
        sum1Sq = sum([pow(self.training_set[p1][it], 2) for it in si])
        sum2Sq = sum([pow(self.training_set[p2][it], 2) for it in si])

        # Sum of the products
        pSum = sum([self.training_set[p1][it] * self.training_set[p2][it] for it in si])

        # Calculate r (Pearson score)
        num = pSum - (sum1 * sum2 / n)
        den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
        if den == 0:
            return 0

        r = num / den

        damp = 1
        if len(si) < self.damp_factor:
            damp = len(si) / float(self.damp_factor)

        return r*damp

    def sim_cosine(self, p1, p2):
        user1 = []
        user2 = []
        for user in self.training_set[p1]:
            if user in self.training_set[p2]:
                user1.append(self.training_set[p1][user] - self.averages[user])
                user2.append(self.training_set[p2][user] - self.averages[user])
        brojnik = sum([prvi * drugi for prvi, drugi in zip(user1, user2)])
        nazivnik = sqrt(sum([pow(prvi, 2) for prvi in user1])) * sqrt(sum([pow(drugi, 2) for drugi in user2]))
        if nazivnik == 0.0:
            return 0.0
        rezultat = brojnik / nazivnik
        damp = 1
        if len(user1) < self.damp_factor:
            damp = len(user1) / float(self.damp_factor)
        return rezultat*damp

    def load_data(self, path='podaci/prefs.csv'):
        movies = {}
        for line in open('podaci/movies.csv'):
            (movie_id, name) = line.strip().split(',', 1)
            if ', ' in name:
                name = name.split(', ')
                name = name[1] + " " + name[0]
            movies[movie_id] = name
            # Load data
        for line in open(path):
            (user, movieid, rating) = line.split(',')
            self.training_set.setdefault(user, {})
            #self.training_set[user][movies[movieid]] = float(rating)
            self.training_set[user][movieid] = float(rating)
        self.training_set = self.transformPrefs()

    def transformPrefs(self):
        result = {}
        for person in self.training_set:
            for item in self.training_set[person]:
                result.setdefault(item, {})

                # Flip item and person
                result[item][person] = self.training_set[person][item]
        return result


class SlopeOne(object):
    def __init__(self):
        self.diffs = {}
        self.freqs = {}
        self.prefs = {}

    def load_model(self):
        prefs = cache.get('prefs')
        if prefs:
            self.prefs = prefs
        else:
            with open('prefs.p', 'rb') as fp:
                data = pickle.load(fp)
            self.prefs = data
            cache.set('prefs', data, 300)
        diffs = cache.get('diffs')
        if diffs:
            self.diffs = diffs
        else:
            with open('diffs.p', 'rb') as fp:
                data = pickle.load(fp)
            self.diffs = data
            cache.set('diffs', data, 300)
        freqs = cache.get('freqs')
        if freqs:
            self.freqs = freqs
        else:
            with open('freqs.p', 'rb') as fp:
                data = pickle.load(fp)
            self.freqs = data
            cache.set('freqs', data, 300)

    def calculate_for_user(self, userprefs):
        preds, freqs = {}, {}
        for item, rating in userprefs.iteritems():
            for diffitem, diffratings in self.diffs.iteritems():
                try:
                    freq = self.freqs[diffitem][item]
                except KeyError:
                    continue
                if freq < 50:
                    continue
                preds.setdefault(diffitem, 0.0)
                freqs.setdefault(diffitem, 0)
                preds[diffitem] += freq * (diffratings[item] + rating)
                freqs[diffitem] += freq
        lista = {item: (value / freqs[item])
                 for item, value in preds.iteritems()
                 if item not in userprefs and freqs[item] > 0}
        return lista

    def load_training_data(self, userdata):
        self.ratings = userdata.copy()
        for ratings in userdata.itervalues():
            for item1, rating1 in ratings.iteritems():
                self.freqs.setdefault(item1, {})
                self.diffs.setdefault(item1, {})
                for item2, rating2 in ratings.iteritems():
                    self.freqs[item1].setdefault(item2, 0)
                    self.diffs[item1].setdefault(item2, 0.0)
                    self.freqs[item1][item2] += 1
                    self.diffs[item1][item2] += rating1 - rating2
        for item1, ratings in self.diffs.iteritems():
            for item2 in ratings:
                ratings[item2] /= self.freqs[item1][item2]

    def predict_for_test_data(self, training_data, test_data):
        for test_user, test_ratings in test_data.iteritems():
            computed_ratings = self.predict(training_data[test_user])
            for movie_name in test_ratings.keys():
                rating = computed_ratings.get(movie_name, None)
                if not rating:
                    continue
                if rating > 5.0:
                    rating = 5.0
                self.ratings[test_user][movie_name] = rating
        return self.ratings

    def split_dataset(self, training_set_percent=80):
        movies = {}
        for line in open('podaci/movies.csv'):
            (movie_id, name) = line.strip().split(',', 1)
            if ', ' in name:
                name = name.split(', ')
                name = name[1] + " " + name[0]
            movies[movie_id] = name
        training = {}
        testing = {}
        count = 0
        training_set_items = training_set_percent * 100
        for line in open('podaci/prefs.csv'):
            count += 1
            (user, movieid, rating) = line.split(',')
            if count > training_set_items:
                training.setdefault(user, {})
                training[user][movies[movieid]] = float(rating)
            else:
                testing.setdefault(user, {})
                testing[user][movies[movieid]] = float(rating)
        return (training, testing)

    def evaluate(self, predicted, testing):
        real_ratings = []
        predicted_ratings = []
        for user, movie_ratings in testing.iteritems():
            for movie_name, rating in movie_ratings.iteritems():
                print movie_name
                predicted_rating = predicted[user].get(movie_name, None)
                if not predicted_rating:
                    continue
                predicted_ratings.append(predicted_rating)
                real_ratings.append(rating)
        print real_ratings
        print predicted_ratings
        return meanabs(real_ratings, predicted_ratings)
