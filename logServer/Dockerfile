FROM ubuntu:22.04

WORKDIR /app

# Install Python 3, pip, and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    add-apt-repository ppa:gijzelaar/snap7 && \
    apt-get update && \
    apt-get install -y libsnap7-1 libsnap7-dev

# Install python-snap7
RUN pip3 install python-snap7==1.3

# Copy project source code
COPY ./src /app/src

# Install Python requirements (adjust the path if needed), and reinstall flask and jinja2
RUN pip3 install --no-cache-dir -r /app/src/requirements.txt && \
    pip3 install --no-cache-dir --force-reinstall Flask Jinja2
# Command to execute the application
CMD ["python3", "/app/src/honeypotLogServer/logArchiveServerApp.py"]

EXPOSE 5004