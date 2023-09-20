GCP_PROJECT_ID = machine-teaching-347613
GCP_APPLICATION_NAME = machine-teaching-app

IMAGE_DESTINATION = gcr.io/$(GCP_PROJECT_ID)/$(GCP_APPLICATION_NAME)

# GIT COMMIT ID
VERSION=$(shell (git rev-parse HEAD))

up:
	mkdir -p ./machine-teaching-db/data
	sh ./machine-teaching-db/dump.sh
	docker-compose up

run:
	@echo "Version ID: $(VERSION)";
	docker build --tag $(IMAGE_DESTINATION):$(VERSION) .
	docker run  --env-file .env -p 8080:8080 $(IMAGE_DESTINATION):$(VERSION)
		
deploy-gcp:
	@echo "Version ID: $(VERSION)";
	docker build --tag $(IMAGE_DESTINATION):$(VERSION) .
	docker push $(IMAGE_DESTINATION):$(VERSION)
	@echo "Image submitted to destination repository :)"
		
run-docker:
	docker build --tag $(IMAGE_DESTINATION):$(VERSION) .
	docker run -it --env-file .env -p 8020:8020 $(IMAGE_DESTINATION):$(VERSION)
