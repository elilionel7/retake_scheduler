# retake_scheduler.

A simple tool to help students easily reschedule missed exams and tests with their instructors.

run: docker compose up --build

## remove container, image and volumes

docker compose down
docker compose down -v
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker system prune -a --volumes -f

## Make startup executable

`chmod +x startup.sh`

remove migrations

`rm -rf migrations/`

Stage all deleted files for removal
git ls-files --deleted -z | xargs -0 git rm

# Commit the changes

git commit -m "Remove deleted files from repository"

remove untrack directory
git clean -fd
