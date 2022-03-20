

build:
	docker build . --tag machineteaching_default

run:
	docker run -it -p 8020:8020 machineteaching_default

deploy:
	heroku container:push web --app machine-teaching-ufrj
	heroku container:release web --app machine-teaching-ufrj