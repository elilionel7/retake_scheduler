# retake_scheduler.
A simple tool to help students easily reschedule missed exams and tests with their instructors.

run: docker compose up --build

## remove container, image and volumes
docker compose down
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker system prune -a --volumes -f

## Make startup executable
chmod +x startup.sh
