# Python PLC Honeypot User Manual

![](doc/img/logo.png)

This manual will show how to deploy the honeypot system in your environment and use the honeypot for some possible attack detection. This document  will show an example of deploying a simple honey pot with two 1-to-1 emulator and controller with different protocol and use this honey pot to show how to detect the attacker's false data injection attack path. 

**Table of Contents**

[TOC]

------

### Honeypot Deployment

To deploy the honeypot system, you need at least 6 VMs to build 2 isolated network with 2 network switches. For each PLC controller and emulator VM, they need 2 network interface to join in the **OT Honeypot Network** and the **Orchestration Network**. The network topology is shown below:

![](doc/img/um/um_s01.png)

All the VMs OS we can use the Ubuntu22.04 and for the deploy sequence, please follow below table:

| VM Name | Deploy Sequence | Honeypot IP | Orchestration IP |      |
| ------- | --------------- | ----------- | ---------------- | ---- |
|         |                 |             |                  |      |
|         |                 |             |                  |      |
|         |                 |             |                  |      |
|         |                 |             |                  |      |
|         |                 |             |                  |      |
|         |                 |             |                  |      |
|         |                 |             |                  |      |

