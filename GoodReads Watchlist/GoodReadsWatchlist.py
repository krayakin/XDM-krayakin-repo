from xdm.plugins import *
import requests
import hashlib
import json


baseURL = 'http://www.goodreads.com'
movieWatchlistURL = baseURL + "user/watchlist/movies.json/"
unwatchlistMovieURL = baseURL + "movie/unwatchlist/"

showWatchlistURL = baseURL + "user/watchlist/shows.json/"
unwatchlistShowURL = baseURL + "show/unwatchlist/"

class goodreadsWatchlist(MediaAdder):
    version = "0.1"
    identifier = "com.krayakin.goodreadswatchlist"
    addMediaTypeOptions = False
    screenName = 'GoodReads Watchlist'
    _config = {'apikey': '',
               'watchtag': 'toread'}
    config_meta = {'plugin_desc': 'Add books from your http://www.goodreads.com watchlist',
                   'watchtag': {'human': 'Tag assigned to books to download'}}

    types = ['de.lad1337.movies']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def runShedule(self):
        if not (self.c.username or self.c.password or self.c.apikey):
            return []
        out = []

        shows = self._getWatchlist(showWatchlistURL, self.c.username, self.c.password, self.c.apikey)
        for show in shows:
            additionalData = {}
            additionalData['tvrage_id'] = show['tvrage_id']
            out.append(self.Media('de.lad1337.books',
                                  show['tvdb_id'],
                                  'tvdb',
                                  'Show',
                                  show['title'],
                                  additionalData=additionalData))
        return out

    def successfulAdd(self, mediaList):
        """media list is a list off all the stuff to remove
        with the same objs that where returned in runShedule() """
        if self.c.remove_movies and len(mediaList):
            return self._removeFromWatchlist(self.c.username, self.c.password, self.c.apikey, mediaList)
        return True

    # get the movie watchlist
    def _getWatchlist(self, watchURL, username, password, apikey):
        url = self._makeURL(watchURL, apikey, username)
        log.debug("Calling goodreads url: %s" % url, censor={apikey: 'apikey', username: 'username'})
        try:
            r = requests.get(url, auth=(username, self._hash(password)))
            return r.json()
        except:
            return []

    def _removeFromWatchlist(self, username, password, apikey, mediaList):
        result = True
        if self.c.remove_movies:
            goodreadsMovieList = []
            for movie in mediaList:
                if movie.elementType == "Movie":
                    goodreadsMovieList.append({'tmdb_id': movie.additionalData['tmdb_id'],
                                           'imdb_id': movie.additionalData['imdb_id']
                                           })
            result = self._removeItemsFromWatchlist(unwatchlistMovieURL, username, password, apikey, {"movies": goodreadsMovieList})
        if self.c.remove_shows:
            goodreadsShowList = []
            for show in mediaList:
                if show.elementType == "Show":
                    goodreadsShowList.append({'tvdb_id': show.externalID})
            result = result == self._removeItemsFromWatchlist(unwatchlistShowURL, username, password, apikey, {"shows": goodreadsShowList})
        return result

    def _removeItemsFromWatchlist(self, unwatchlistURL, username, password, apikey, goodreadsData):
        url = self._makeURL(unwatchlistURL, apikey, "")
        log.info('Removing items from goodreads watchlist %s' % goodreadsData)
        postdata = {'username': username,
                    'password': self._hash(password)}
        postdata.update(goodreadsData)
        try:
            r = requests.post(url, data=json.dumps(postdata))
            try:
                return r.json()['status'] == 'success'
            except ValueError:
                return False
        except:
            return False

    # construct the url
    def _makeURL(self, url, apiKey, username):
        result = url + apiKey
        if username != "":
            result += "/" + username
        return result

    # SHA1 hash
    def _hash(self, value):
        m = hashlib.sha1()
        m.update(value)
        return m.hexdigest()