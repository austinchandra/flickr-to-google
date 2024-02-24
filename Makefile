install:
	pip3 install -r requirements.txt

directory:
	mkdir -p outputs
	python3 src/photoset_directory.py

transfer:
	python3 src/photoset_transfer.py
