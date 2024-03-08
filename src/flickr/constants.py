from enum import StrEnum

class Endpoints(StrEnum):
    OAUTH = 'https://www.flickr.com/services/oauth'
    REST = 'https://www.flickr.com/services/rest/'

QUERIES_PER_PAGE = 500
