

up:
	docker-compose up

deploy:
	heroku container:push web --app machine-teaching-ufrj
	heroku container:release web --app machine-teaching-ufrj