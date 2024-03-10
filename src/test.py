import asyncio
import flickrapi

from flickr.query import query

def oauth():
    api_key = u'55256e22b7cd1f302d2d2991e17ed570'
    api_secret = u'570ec2b4b241dbdd'

    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
    flickr.authenticate_via_browser(perms='read')

    response = flickr.test.login()
    print(response)

async def test():
    response = await query(
        method='flickr.test.login'
    )

    print(response)

oauth()
# asyncio.run(test())

