# Requirements

- Python version 3.11+
- Flickr API account
- Google API account

# Setup

Install the project and its dependencies:

```
git clone https://github.com/0a1c/flickr-to-google
cd flickr-to-google
source venv/bin/activate
make install
```

# Credentials

Create a Flickr API key and secret ([instructions](https://www.flickr.com/services/api/misc.api_keys.html))
and include them in a `flickr_credentials.json` file:

```
{
    "api_key": <api_key>,
    "api_secret": <api_secret>
}
```

Create a Google project ([instructions](https://developers.google.com/photos/library/guides/get-started))
and download the generated credentials file. It should contain the following fields:

```
{
    "installed": { "client_id" : <client_id>, "project_id": <project_id>, ... }
}
```

# Running

### 1. Set the project configuration
Set the project configuration using the Flickr user's NSID and the credential files.

If the user has not set a username alias, the NSID is located in the URL for the user's profile.
Otherwise, the NSID can be located in the sidebar of an API Explore Page such as
[flickr.people.getInfo](https://www.flickr.com/services/api/explore/flickr.people.getInfo).

```
python3 flickr-to-google set-config \
-u <flickr_user_id> \
-f <path/to/flickr_credentials.json> \
-g <path/to/google_credentials.json>
```

### 2. Authenticate accounts for both platforms

```
python3 flickr-to-google authenticate
```

### 3. Initialize the directory

```
python3 flickr-to-google create-directory
```

### 4. Populate the directory

```
python3 flickr-to-google populate-directory
```

### 5. Create the albums on Google

```
python3 flickr-to-google create-albums
```

### 5. Upload the photos to Google

```
python3 flickr-to-google upload-photos
```

