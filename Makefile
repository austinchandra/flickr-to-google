install:
	pip3 install -r requirements.txt

directory:
	rm -rf outputs
	python3 src/flickr/directory.py

authenticate-google:
	rm -f token.json
	python3 src/google/authenticate.py

albums:
	python3 src/google/albums.py

photos:
	python3 src/google/photos.py
