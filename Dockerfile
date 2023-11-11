FROM python:3.9-slim

# Update apt packages and install necessary utilities
RUN apt-get update \
    && apt-get install -y wget gnupg2 ca-certificates unzip xvfb curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# Set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /project-1-web-application-design-group17-jigglies
COPY . /project-1-web-application-design-group17-jigglies
RUN pip install --no-cache-dir -r requirements.txt

# Default behaviour but will get overridden by docker-compose
CMD ["flask", "run", "--reload", "--host=0.0.0.0"]
