from xdm.plugins import *
import requests


baseURL = 'http://www.goodreads.com'
#movieWatchlistURL = baseURL + "user/watchlist/movies.json/"
#unwatchlistMovieURL = baseURL + "movie/unwatchlist/"

#showWatchlistURL = baseURL + "user/watchlist/shows.json/"
#unwatchlistShowURL = baseURL + "show/unwatchlist/"

class goodreadsWatchlist(MediaAdder):
    version = "0.1"
    identifier = "com.krayakin.goodreadswatchlist"
    addMediaTypeOptions = False
    screenName = 'GoodReads Watchlist'
    _config = {'apikey': '',
               'watchtag': 'toread'}
    config_meta = {'plugin_desc': 'Add books from your http://www.goodreads.com watchlist',
                   'watchtag': {'human': 'Tag assigned to books to download'}}

    types = ['de.lad1337.books']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def runShedule(self):
        if not (self.c.apikey):
            return []
        out = []


        searchUrl = '%s/search.xml' % baseURL
        #r = requests.get(url, params = payload)
        #shows = self._getWatchlist(showWatchlistURL, self.c.username, self.c.password, self.c.apikey)
        #for show in shows:
        #    additionalData = {}
        #    additionalData['tvrage_id'] = show['tvrage_id']
        #    out.append(self.Media('de.lad1337.books',
        #                          show['tvdb_id'],
        #                          'tvdb',
        #                          'Show',
        #                          show['title'],
        #                          additionalData=additionalData))
        return out

    #def successfulAdd(self, mediaList):
        #"""media list is a list off all the stuff to remove
        #with the same objs that where returned in runShedule() """
        #"""if self.c.remove_movies and len(mediaList):
        #    return self._removeFromWatchlist(self.c.username, self.c.password, self.c.apikey, mediaList)
        #return True """

    # get the movie watchlist
    def _getWatchlist(self, watchURL, apikey):
        url = self._makeURL(watchURL, apikey)

        payload = {
                   'key': self.c.api_key}
        log.debug("Calling goodreads url: %s" % url, censor={key: 'key'})
        try:
            r = requests.get(url, params = payload)
            return r.json()
        except:
            return []

