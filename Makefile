index-movies:
	python3 src/index/main.py movie_plots.json $(file_dir)

index-seuss:
	python3 src/index/main.py dr_seuss_lines.json $(file_dir)

query:
	python3 src/query/main.py $(file_dir) '$(query)'

install:
	pip3 install -r requirements.txt

download-nltk:
	python3 src/download_nltk.py