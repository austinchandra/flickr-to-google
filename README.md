Transfer all photos and videos from Flickr to Google Photos, preserving image quality and album
structure.

# Setup

## Installation

Install the project and its dependencies:

```
git clone https://github.com/0a1c/flickr-to-google
cd flickr-to-google
python3 -m venv venv
source venv/bin/activate
make install
```

## Credentials

Create and configure the requisite credential files needed to authenticate API requests:

### Flickr API

Create an API key for authenticating Flickr API requests as shown
[here](https://www.flickr.com/services/api/misc.api_keys.html).
Then, format the key and secret in a `flickr_credentials.json` file as below. Keep this file
location on-hand.

```
{
    "api_key": <api_key>,
    "api_secret": <api_secret>
}
```

### Google API

Create a Google Cloud project using the instructions
[here](https://developers.google.com/photos/library/guides/get-started).

Download the client credentials file and keep its location on-hand. This file should have the
following fields:

```
{
    "installed": { "client_id" : <client_id>, "project_id": <project_id>, ... }
}
```

# Usage

## 1. Specify initial parameters

Set the project's configuration by providing the Flickr user's NSID, Flickr cookies, and the
credential files from the previous step.

The following steps assume you are authenticated on Flickr.

To find the NSID, navigate to your Flickr profile. If you have not set a username alias, your NSID
is located in the URL (e.g., "200000000@N02"). Otherwise, find your NSID on an API Explore Page,
such as [flickr.people.getInfo](https://www.flickr.com/services/api/explore/flickr.people.getInfo),
where it is located in the sidebar.

To find your Flickr cookies, go to Flickr's website, then open the list of cookies in your browser's
developer menu. On Chrome, this can be found under Application -> Cookies -> https://flickr.com.

Copy the values for `cookie_session` and `cookie_epass` for the command. These are required in order
to download full-quality videos.

```
python3 flickr-to-google set-config \
-u <flickr_user_id> \
--flickr-keys-path <path/to/flickr_credentials.json> \
--google-keys-path <path/to/google_credentials.json> \
--flickr-cookie-session <cookie_session> \
--flickr-cookie-epass <cookie_epass> \
```

## 2. Authenticate accounts for both platforms

Provide the authentication tokens necessary to perform read requests from Flickr and write requests
to Google Photos.

Note that in order to provide approval to authenticate your Google account, your email must be
listed as a test account for your Google project's OAuth-enabled users. If it is not already set,
add your email under the "OAuth consent screen" for your project.

```
python3 flickr-to-google authenticate
```

## 3. Initialize the directory

Set up a directory that tracks your Flickr photo information, as well as the download or upload
status for each photo.

Use caution if you decide to re-run this step for any reason, as doing so will reset all cached
information from subsequent steps, leading to potentially unexpected behavior such as duplicate
albums.

```
python3 flickr-to-google create-directory
```

## 4. Populate the directory

Populate the directory created with the photo metadata required to download and transfer the images.

This step, and the remainder, are idempotent and can be safely re-run on failure.

```
python3 flickr-to-google populate-directory
```

## 5. Create the albums on Google

```
python3 flickr-to-google create-albums
```

## 6. Upload the photos to Google

```
python3 flickr-to-google upload-photos
```

## 7. (Optional) Download the photos to disk

Instead of (or alongside) streaming the photos directly from Flickr to Google, it is possible to
download the information to disk.

Use the flag `download-all` to indicate whether photos already downloaded should be re-downloaded
(e.g. on moving the directory).

```
python3 flickr-to-google download-photos -p <path/to/download> --download-all <true or false>
```
