from requests_oauthlib import OAuth1Session

import xmltodict
import json

from xdm.plugins import *


baseURL = 'http://www.goodreads.com'


class goodreadswatchlist(MediaAdder):
    version = "0.216"
    identifier = "com.krayakin.goodreadswatchlist"
    addMediaTypeOptions = False
    screenName = 'GoodReads Watchlist'
    _config = {'apikey': '',
               'apisecret': '',
               'request_token_key': '',
               'request_token_secret': '',
               'oauth_verifier': '',
               'oauth_token': '',
               'oauth_secret': '',
               'authurl': '',
               'responseurl': '',
               'watchtag': 'toread',
               'userid': ''
    }

    config_meta = {'plugin_desc': 'Add books from your http://www.goodreads.com watchlist',
                   'watchtag': {'human': 'Tag assigned to books to download'},
                   'userid': {'human': 'GoodReads UserID'}
    }

    types = ['de.lad1337.books']

    def __init__(self, instance='Default'):
        MediaAdder.__init__(self, instance=instance)

    def runShedule(self):
        if not self.c.apikey:
            return []

        request_token_url = 'http://www.goodreads.com/oauth/request_token'
        base_authorization_url = 'http://www.goodreads.com/oauth/authorize'
        access_token_url = 'http://www.goodreads.com/oauth/access_token'

        oauth = OAuth1Session(
            client_key=self.c.apikey,
            client_secret=self.c.apisecret
        )

        if not self.c.authurl:
            # obtain the resource owner client tokens
            fetch_response = oauth.fetch_request_token(request_token_url)

            self.c.request_token_key = fetch_response.get('oauth_token')
            self.c.request_token_secret = fetch_response.get('oauth_token_secret')

            self.c.authurl = oauth.authorization_url(base_authorization_url)
            return []

        if not self.c.oauth_token:
            oauth_response = oauth.parse_authorization_response(self.c.responseurl)

            self.c.oauth_verifier = oauth_response.get('oauth_verifier')
            oauth = OAuth1Session(
                client_key=self.c.apikey,
                client_secret=self.c.apisecret,
                resource_owner_key=self.c.request_token_key,
                resource_owner_secret=self.c.request_token_secret,
                verifier=self.c.oauth_verifier,
            )

            oauth_tokens = oauth.fetch_access_token(access_token_url)
            self.c.oauth_token = oauth_tokens.get('oauth_token')
            self.c.oauth_secret = oauth_tokens.get('oauth_token_secret')

        out = []

        oauth = OAuth1Session(
            client_key=self.c.apikey,
            client_secret=self.c.apisecret,
            resource_owner_key=self.c.oauth_token,
            resource_owner_secret=self.c.oauth_secret,
            verifier=self.c.oauth_verifier,
        )

        payload = {'v': 2,
                   'id': self.c.userid,
                   'format': 'xml',
                   'shelf': self.c.watchtag,
                   'per_page': 200,
        }

        searchUrl = '%s/review/list' % baseURL
        r = oauth.get(searchUrl, params=payload)

        books = xmltodict.parse(r.text)['GoodreadsResponse']['reviews']['review']
        #log.debug(json.dumps(books))

        #title = ''
        #author = ''
        #cover_image = ''
        #rating = ''

        for book in books:
            log.debug('ID:%s Title:%s Author:%s Image:%s Rating:%s' % (book['book']['id'], book.get('title','<NULL>'), book['authors']['author']['name'], book.get('image_url','<NULL>'), book.get('average_rating',0)))

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
