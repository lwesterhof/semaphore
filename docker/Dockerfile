# Grab Python image.
FROM python:3.9.12-slim-bullseye

WORKDIR /semaphore

# Upgrade pip.
RUN pip install --upgrade pip

# Install Semaphore.
RUN pip install --no-cache-dir semaphore-bot==v0.14.0

# Copy bot script.
COPY bot.py bot.py

# Start the bot.
CMD ["python", "bot.py"]
