from flickr import flickr

def query_photoset_list(user_id):
    def inner(page, per_page):
        photosets = flickr.photosets.getList(page=page, per_page=per_page, user_id=user_id)
        data = [parse_photoset_data(photoset) for photoset in photosets['photosets']['photoset']]
        pages = photosets['photosets']['pages']

        return (data, pages)

    return query_paginated(inner)

def query_photoset_photos(user_id, photoset_id):
    def inner(page, per_page):
        photo_ids = flickr.photosets.getPhotos(
            photoset_id=photoset_id,
            page=page,
            per_page=per_page,
            user_id=user_id,
        )

        ids = [photo['id'] for photo in photo_ids['photoset']['photo']]
        pages = photo_ids['photoset']['pages']

        data = []

        for pid in ids:
            photo = flickr.photos.getInfo(photo_id=pid)
            print(photo)
            data.append(parse_photoset_photo(photo['photo']))

        return (data, pages)

    return query_paginated(inner)

def parse_photoset_data(photoset):
    data = {}

    data['id'] = photoset['id']
    data['title'] = photoset['title']['_content']
    # TODO: Parse UNIX.
    data['created'] = photoset['date_create']
    data['updated'] = photoset['date_update']
    data['photos'] = photoset['photos']
    # TODO: Assuming there are no videos; or, that they do not require any
    # changes in logic.
    data['videos'] = photoset['videos']

    return data

def parse_photoset_photo(photo):
    data = {}

    data['id'] = photo['id']
    data['title'] = photo['title']['_content']
    data['description'] = photo['description']['_content']
    data['posted'] = photo['dates']['posted']

    return data

def query_paginated(query):
    results = []
    page = 1
    per_page = 500

    # Can parallelize this since the page limit can be ascertained beforehand,
    # but use a sequential solution for simplicity. Throws exceptions.

    while True:
        (page_results, page_limit) = query(page, per_page)
        results += page_results

        if page == page_limit:
            break

        page += 1

    return results
