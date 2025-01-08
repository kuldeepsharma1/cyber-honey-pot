
# Python PLC Honeypot Project

The **Python PLC Honeypot Project** is a distributed cybersecurity solution designed to simulate SCADA (Supervisory Control and Data Acquisition) network behaviors between Programmable Logic Controllers (PLCs) and Human-Machine Interfaces (HMIs). This honeypot replicates an Operational Technology (OT) environment to attract and analyze potential cyberattacks. 

The project does not require specialized OT hardware; it is entirely virtualized, allowing users to run the system on Virtual Machines (VMs). However, the platform supports integration with physical OT hardware if desired. 

### Objectives:
1. **Data Collection**: Gather attack data and Digital Forensics and Incident Response (DFIR) datasets.
2. **Threat Analysis**: Study attack techniques in industrial environments.
3. **Blue Team Training**: Provide defenders with a safe environment to monitor, analyze, and respond to cyber threats.

---

## Features
- Simulates SCADA network communication between PLCs and HMIs.
- Distributed, modular architecture supporting VMs or hardware integration.
- Attack data collection and visualization.
- Fully containerized deployment using Docker.
- Scalable and adaptable to various OT setups.

---

## Dockerization Steps

Follow these steps to containerize the Python PLC Honeypot components. Each component is modularized to enable flexible deployment.

### Prerequisites
Before starting, ensure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)



### 1. Building Docker Images

#### 1.1 Monitor VM
This component monitors system activity and gathers logs.

```bash
cd monitor
docker build -t monitor .
```

#### 1.2 Log Server
The `logServer` component is responsible for storing and processing logs generated by the honeypot.

```bash
cd logServer
docker build -t logserver .
```

#### 1.3 PLC Emulator
The `plcEmulator` simulates the functionality of a Programmable Logic Controller.

```bash
cd plcEmulator
docker build -t plcemulator .
```

#### 1.4 PLC Controller
The `plcController` manages communication and commands sent to the PLC Emulator.

```bash
cd plcController
docker build -t plccontroller .
```

#### 1.5 S7 Communication PLC Emulator
This component emulates Siemens S7 communication protocol behavior.

```bash
cd s7commPlcEmulator
docker build -t splcemulator .
```

#### 1.6 S7 Communication Controller
The `s7commcontroller` oversees interactions with the S7 communication protocol emulator.

```bash
cd s7commcontroller
docker build -t splccontroller .
```
```bash
# Run one command from below first run to run in interactive mode or second to run in Background
docker compose up 

docker compose up -d 
```
---

## Summary
After completing the steps above, you will have built Docker images for all components of the Python PLC Honeypot. These images enable the deployment of a simulated OT environment, allowing for attack analysis, data collection, and training in a secure, virtualized setting.

For additional details on deployment and usage, refer to the project documentation or contact the project maintainers.
