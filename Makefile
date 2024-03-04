install:
	pip3 install -r requirements.txt

directory:
	rm -rf outputs
	python3 src/flickr/directory.py

authenticate-google:
	python3 src/google/authenticate.py

albums:
	python3 src/google/albums.py

photo-bytes:
	python3 src/google/photo_bytes.py

photo-upload:
	python3 src/google/photo_upload.py

transfer:
	make albums
	make photo-bytes
	make photo-upload

all:
	make directory
	make transfer
