FROM ubuntu:22.04

WORKDIR /app

# Install Python 3, pip, and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    add-apt-repository -y ppa:gijzelaar/snap7 && \
    apt-get update && \
    apt-get install -y libsnap7-1 libsnap7-dev && \
    apt-get clean

# Install python-snap7 and other Python dependencies
RUN pip3 install --no-cache-dir python-snap7==1.3 Flask Jinja2 flask-login

# Copy project source code
COPY ./src /app/src

# Install Python requirements (adjust the path if needed)
RUN pip3 install --no-cache-dir -r /app/src/requirements.txt

# Expose necessary ports
EXPOSE 5002

# Add a script to run both applications
RUN chmod +x /app/src/entry.sh

# Command to execute the entrypoint script
CMD ["/app/src/entry.sh"]
