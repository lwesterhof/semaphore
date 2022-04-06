# Grab signald image.
FROM signald/signald:0.17.0

WORKDIR /root

# Update and install pip.
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip

# Install Semaphore library.
RUN pip install --no-cache-dir semaphore-bot==v0.13.0

# Set socket path for signald.
RUN mkdir /var/run/signald
RUN echo "socketpath: /var/run/signald/signald.sock" >> /root/.config/signaldctl.yaml

# Copy bot and start script.
COPY bot.py /root
COPY start_bot.sh /root

# Start signald.
CMD signald --trust-new-keys > /var/log/signald.log
