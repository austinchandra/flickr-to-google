## If all photos are public; can use getPublicPhotos (with pagination);
## otherwise, require OAuth -> Get Collections -> Get Photo IDs -> Get Sizes

## 1. Download photo ids (write to disk); throw on errors, as this is likely to
##    succeed at once (given the low amount of information).
## 2. Given list of photo ids (from url on disk), pull image contents, for each,
##    then write these to Google; build a set of of outputs of successes; on any
##    successive attempt, include these success lists to exclude them as having
##    been completed (can alternatively query Google before downloading each one);
##    this seems more correct.

## 1. Download a list of photo IDs from Flickr; for each one, query Google to see
## if it is there (given an overlap in the name or identifier); if not, download
## the photo from Flickr and upload it to Google. This can be repeated indefinitely,
## as it is idempotent.

## 1. Download a list of photo IDs from Flickr, and write these to disk.
## 2. Take in a list of photo IDs from Flickr, then for each, upload them to Google;
## write down failures on disk; these will serve as the next input.
##
## This improves on the above in that it can selectively run against inputs that failed;
## can retain idempotence, if desired, but the ability to query selective inputs is
## valuable. Can use threading on the upload/download process.

#import requests
#from flickr import flickr

#user_id = '200072260@N02'

#images_per_page = '500'

#photo_ids = []

## TODO: query until there are no more images returned
## TODO: if there are private photos, include OAuth authentication
#for page in range(1, 2):
#    photos = flickr.people.getPublicPhotos(user_id=user_id, page=page, per_page=images_per_page)
#    ids = [photo['id'] for photo in photos['photos']['photo']]

#    photo_ids += ids

## image = flickr.photos.getSizes(photo_id='53528014468')
#print(photo_ids)
## print(image)

#for photo_id in photo_ids:
#    image = flickr.photos.getSizes(photo_id=photo_id)
#    sizes = image['sizes']['size']
#    original = sizes[-1]
#    assert original['label'] == 'Original'
#    url = original['source']
#    print(url)

#    # TODO: upload data to Drive
#    data = requests.get(url).content
