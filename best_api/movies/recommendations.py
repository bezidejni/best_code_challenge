import cPickle as pickle
from math import sqrt
from django.core.cache import cache

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0

    r = num / den

    damp=1
    if len(si) < 25:
        damp = len(si) / 25.0

    return r*damp


def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


averages = {}


def calculate_averages(prefs):
    inverted = transformPrefs(prefs)
    for user, ratings in inverted.iteritems():
        if not user in averages:
            total_ratings = sum([rating for title, rating in ratings.iteritems()])
            total_items = len(ratings)
            averages[user] = total_ratings / total_items


def sim_cosine(prefs, p1, p2):
    user1 = []
    user2 = []
    for user in prefs[p1]:
        if user in prefs[p2]:
            user1.append(prefs[p1][user] - averages[user])
            user2.append(prefs[p2][user] - averages[user])
    brojnik = sum([prvi * drugi for prvi, drugi in zip(user1, user2)])
    nazivnik = sqrt(sum([pow(prvi, 2) for prvi in user1])) * sqrt(sum([pow(drugi, 2) for drugi in user2]))
    if nazivnik == 0.0:
        return 0.0
    rezultat = brojnik / nazivnik
    damp=1
    if len(user1) < 50:
        damp = len(user1) / 50.0
    return rezultat*damp


# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_cosine):
    if not averages:
        calculate_averages(prefs)
    scores = [(similarity(prefs, person, other), other)
              for other, ratings in prefs.iteritems() if other != person and len(ratings) > 5]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    best_critics = topMatches(prefs, person, n=50)
    for sim, other in best_critics:
        for item in prefs[other]:

            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings


def calculateSimilarItems(prefs, n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result = {}
    # Invert the preference matrix to be item-centric
    c = 0
    for item in prefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(prefs))
        # Find the most similar items to this one
        scores = topMatches(prefs, item, n=n, similarity=sim_cosine)
        result[item] = scores
    return result


def getRecommendedItems(itemMatch, user):
    userRatings = user
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():

        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings:
                continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings


def loadMovieLens(path='podaci/prefs.csv'):
    movies = {}
    for line in open('podaci/movies.csv'):
        (movie_id, name) = line.strip().split(',', 1)
        if ', ' in name:
            name = name.split(', ')
            name = name[1] + " " + name[0]
        movies[movie_id] = name
        # Load data
    prefs = {}
    for line in open(path):
        (user, movieid, rating) = line.split(',')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    prefs = transformPrefs(prefs)
    return prefs


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

    def predict(self, userprefs, num_of_movies=10):
        preds, freqs = {}, {}
        for item, rating in userprefs.iteritems():
            for diffitem, diffratings in self.diffs.iteritems():
                try:
                    freq = self.freqs[diffitem][item]
                except KeyError:
                    continue
                if freq < 10:
                    continue
                preds.setdefault(diffitem, 0.0)
                freqs.setdefault(diffitem, 0)
                preds[diffitem] += freq * (diffratings[item] + rating)
                freqs[diffitem] += freq
        lista = [(value / freqs[item], item)
                 for item, value in preds.iteritems()
                 if item not in userprefs and freqs[item] > 0]
        return sorted(lista, reverse=True)[:num_of_movies]

    def compute(self, userdata):
        #userdata = transformPrefs(userdata)
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
