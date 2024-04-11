GCP_PROJECT_ID = machine-teaching-347613
GCP_APPLICATION_NAME = machine-teaching-webapp

VERSION=$(shell (git rev-parse HEAD)) 

IMAGE_DESTINATION = us-central1-docker.pkg.dev/$(GCP_PROJECT_ID)$(GCP_APPLICATION_NAME)/$(VERSION)

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
