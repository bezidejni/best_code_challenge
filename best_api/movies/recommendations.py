import cPickle as pickle
import itertools
import os
import sys
import traceback
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
            'offset': 0,
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
        """
        Loads the precalculated model from cache or from disk.
        """
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

    def evaluate(self):
        """
        Calculates the MAE between the predicted and test ratings.
        """
        predicted = self.get_full_rating_matrix()
        real_ratings = []
        predicted_ratings = []
        for user, movie_ratings in self.test_set.iteritems():
            for movie_id, rating in movie_ratings.iteritems():
                predicted_user = predicted.get(user, None)
                if not predicted_user:
                    continue
                predicted_rating = predicted_user.get(movie_id, None)
                if not predicted_rating:
                    continue
                predicted_ratings.append(predicted_rating)
                real_ratings.append(rating)
        return meanabs(real_ratings, predicted_ratings)

    def get_recommended_items(self, user):
        """
        Gets top n recommended items based on the user ratings.
        """
        userRatings = user
        scores = {}
        totalSim = {}
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
        return movie_ids[:10]

    def top_matches(self, person):
        """
        Return n best matches for every item based on the user ratings.
        """
        similarity = getattr(self, self.similarity_function)
        if not self.averages:
            self.calculate_averages()
        scores = [(similarity(person, other), other)
                  for other, ratings in self.training_set.iteritems()
                  if other != person and len(ratings) > self.min_num_of_ratings]
        scores.sort()
        scores.reverse()
        return scores[0:self.similar_calculate]

    def calculate_similar_items(self):
        """
        Calculates the most similar items for every item and stores
        that in matrix form.
        """
        c = 0
        for item in self.training_set:
            scores = self.top_matches(item)
            self.similarity_matrix[item] = scores

    def calculate_averages(self):
        """
        Calculate average ratings given by each user, used for normalizing
        the adjusted cosine similiarity method.
        """
        inverted = self.transform_matrix()
        for user, ratings in inverted.iteritems():
            if not user in self.averages:
                total_ratings = sum([rating for title, rating in ratings.iteritems()])
                total_items = len(ratings)
                self.averages[user] = total_ratings / total_items

    def sim_pearson(self, p1, p2):
        """
        Pearson similarity method for determining similarity
        between two items, more info here:
        http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/pear.html
        """
        # Get the list of mutually rated items
        common_ratings = {}
        for item in self.training_set[p1]:
            if item in self.training_set[p2]:
                common_ratings[item] = 1

        # if they are no ratings in common, return 0
        if len(common_ratings) == 0:
            return 0

        # Sum calculations
        num_of_common = len(common_ratings)

        # Sums of all the preferences
        sum1 = sum([self.training_set[p1][it] for it in common_ratings])
        sum2 = sum([self.training_set[p2][it] for it in common_ratings])

        # Sums of the squares
        sum1_sq = sum([pow(self.training_set[p1][it], 2) for it in common_ratings])
        sum2_sq = sum([pow(self.training_set[p2][it], 2) for it in common_ratings])

        # Sum of the products
        product_sum = sum([self.training_set[p1][it] * self.training_set[p2][it] for it in common_ratings])

        # Calculate r (Pearson score)
        nominator = product_sum - (sum1 * sum2 / num_of_common)
        denominator = sqrt((sum1_sq - pow(sum1, 2) / num_of_common) * (sum2_sq - pow(sum2, 2) / num_of_common))
        if denominator == 0:
            return 0

        r = nominator / denominator

        # damping function that lessens the value of items that have few common ratings
        damp = 1
        if len(common_ratings) < self.damp_factor:
            damp = len(common_ratings) / float(self.damp_factor)

        return r*damp

    def sim_cosine(self, p1, p2):
        """
        Adjusted cosine similarity method for determining the
        similarit between two items, more info:
        http://www.stat.osu.edu/~dmsl/Sarwar_2001.pdf
        in section 3.1.3
        """
        user1 = []
        user2 = []
        for user in self.training_set[p1]:
            if user in self.training_set[p2]:
                user1.append(self.training_set[p1][user] - self.averages[user])
                user2.append(self.training_set[p2][user] - self.averages[user])
        nominator = sum([first * second for first, second in zip(user1, user2)])
        denominator = sqrt(sum([pow(first, 2) for first in user1])) * sqrt(sum([pow(second, 2) for second in user2]))

        if denominator == 0.0:
            return 0.0

        rezultat = nominator / denominator

        # damping function that lessens the value of items that have few common ratings
        damp = 1
        if len(user1) < self.damp_factor:
            damp = len(user1) / float(self.damp_factor)
        return rezultat*damp

    def load_data(self, path='podaci/prefs.csv'):
        """
        Loads the user rating data from the prefs.csv file and splits
        the set into training and testing data according to the
        training_set_percent attribute.
        """
        training_set_items = self.training_set_percent * 1000
        test_set_items = 100000 - training_set_items
        test_set_lower_limit = self.offset * test_set_items
        test_set_upper_limit = test_set_lower_limit + test_set_items
        count = 0
        for line in open(path):
            count += 1
            (user, movieid, rating) = line.split(',')
            if test_set_lower_limit < count < test_set_upper_limit:
                self.test_set.setdefault(user, {})
                self.test_set[user][movieid] = float(rating)
            else:
                self.training_set.setdefault(user, {})
                self.training_set[user][movieid] = float(rating)
        self.training_set = self.transform_matrix()

    def transform_matrix(self):
        """
        Transforms the matrix from user-centric to item-centric
        and reverse. Useful because some calculations are easier to perform
        one one type.
        """
        result = {}
        for person in self.training_set:
            for item in self.training_set[person]:
                result.setdefault(item, {})

                # Flip item and person
                result[item][person] = self.training_set[person][item]
        return result

    def get_full_rating_matrix(self):
        """
        Returns the "full" matrix with predicted scores for each (user, item) pair,
        used only for evaluating how good is the algorithm - calculating MAE.
        """
        if not self.similarity_matrix:
            self.calculate_similar_items()
        full_ratings_matrix = {}

        user_based_matrix = self.transform_matrix()
        for movie_id in self.training_set.keys():
            similar = self.similarity_matrix[movie_id]
            for user, ratings in user_based_matrix.iteritems():
                total_rating = 0
                total_sim = 0
                for similarity, similar_id in similar:
                    rating = ratings.get(similar_id, 0)
                    if rating:
                        total_rating += rating * similarity
                        total_sim += similarity
                if total_sim:
                    predicted_rating = total_rating / total_sim
                    full_ratings_matrix.setdefault(user, {})
                    full_ratings_matrix[user][movie_id] = predicted_rating
        return full_ratings_matrix


def evaluator():
    """
    Tries different combinations of algorith parameters and tries to
    calculate the MAE (Mean Average Error) for each (user,item) pair
    between the values from the testing set and calculated/predicted ones.

    """
    min_ratings = (5, 15, 30, 50)
    damp_factors = (1, 10, 30, 50)
    similar_calculates = (5, 25, 50, 75)
    training_set_percentages = (80, 90, 95)

    experiment_count = 0
    for set_percentage in training_set_percentages:
        test_set_size = 100 - set_percentage
        # finds all the offsets that don't go over the limit
        offsets = [i for i in range(50) if (i*test_set_size) <= (100-test_set_size)]
        for (min_rating, damp, similar_calc) in itertools.product(
                min_ratings, damp_factors, similar_calculates):
            experiment_count += 1
            print "Experiment {0}, min_rating:{1}, dump:{2}, similar_calc:{3}, set_percentage:{4}".format(
                experiment_count, min_rating, damp, similar_calc, set_percentage)
            total_mae = 0
            offset_count = 0
            for offset in offsets:
                rec = ItemBasedRecommender(
                    damp_factor=damp,
                    min_num_of_ratings=min_rating,
                    offset=offset,
                    similar_calculate=similar_calc,
                    training_set_percent=set_percentage
                )
                rec.load_data()
                rec.calculate_similar_items()
                try:
                    experiment_mae = rec.evaluate()
                    offset_count += 1

                    total_mae += experiment_mae
                except:
                    print "Experiment {0} failed".format(experiment_count)
                    print traceback.print_tb(sys.exc_info()[2])
                    continue

            total_mae = total_mae / offset_count
            print "MAE: {0}".format(total_mae)
