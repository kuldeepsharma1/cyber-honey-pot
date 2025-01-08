#!/bin/bash

# Start the log archive agent in the background
python3 /app/src/honeypotLogClient/logArchiveAgent.py &

# Start the S7Comm PLC Emulator in the foreground
exec python3 /app/src/s7commPlcController/s7commPlcControllerApp.py