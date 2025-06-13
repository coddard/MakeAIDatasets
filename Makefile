.PHONY: build run run-web run-cli clean

build:
	docker-compose build

run-web:
	docker-compose up web

run-cli:
	docker-compose up cli

run:
	docker-compose up

clean:
	docker-compose down
	docker system prune -f
