install:
	pip3 install -r requirements.txt

clean:
	rm -rf ~/.flickr-to-google/outputs
	rm ~/.flickr-to-google/google_token.json

clean-all:
	rm -rf ~/.flickr-to-google/
