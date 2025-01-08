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
RUN pip install --upgrade flask-login

EXPOSE 5001
# Add a script to run both applications
RUN chmod +x /app/src/entry.sh

# Command to execute the entrypoint script
CMD ["/app/src/entry.sh"]