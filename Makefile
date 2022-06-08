GCP_PROJECT_ID = machine-teaching-347613
GCP_APPLICATION_NAME = machine-teaching-app

IMAGE_DESTINATION = gcr.io/$(GCP_PROJECT_ID)/$(GCP_APPLICATION_NAME)

# GIT COMMIT ID
VERSION=$(shell (git rev-parse HEAD))

up:
	docker-compose up

deploy:
	/home/gxara/Downloads/heroku/bin/heroku container:push web --app machine-teaching-ufrj
	/home/gxara/Downloads/heroku/bin/heroku container:release web --app machine-teaching-ufrj


deploy-gcp:
	@echo "Version ID: $(VERSION)";
	docker build --tag $(IMAGE_DESTINATION):$(VERSION) .
	docker push $(IMAGE_DESTINATION):$(VERSION)
	@echo "Image submitted to destination repository :)"
		
run-docker:
	docker build --tag $(IMAGE_DESTINATION):$(VERSION) .
	docker run -it --env PORT=8020 -p 8020:8020 $(IMAGE_DESTINATION):$(VERSION)
