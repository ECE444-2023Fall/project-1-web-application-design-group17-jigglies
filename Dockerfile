FROM python:3.9-slim

WORKDIR /project-1-web-application-design-group17-jigglies
COPY . /project-1-web-application-design-group17-jigglies
RUN pip install --no-cache-dir -r requirements.txt


# Default behaviour but will get overridden by docker-compose
CMD ["flask", "run", "--reload", "--host=0.0.0.0"]
