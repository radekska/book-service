# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

DOCKER_COMPOSE=${PWD}/docker/docker-compose.yml

all: down build up test black

build:
	docker-compose -f ${DOCKER_COMPOSE} build --no-cache

up:
	docker-compose -f ${DOCKER_COMPOSE} up -d

down:
	docker-compose -f ${DOCKER_COMPOSE} kill && docker system prune -f --volumes

logs:
	docker-compose -f ${DOCKER_COMPOSE} logs app | tail -100

test:
	black -l 86 --check .
	docker-compose -f ${DOCKER_COMPOSE} exec app pytest -v \
			--asyncio-mode=strict \
			--cov-config="tests/.coveragerc" \
			--cov=src/ tests/

black:
	black -l 86 .
