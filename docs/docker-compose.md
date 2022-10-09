# Install SAPIENTA in docker-compose Mode

This guide outlines the process for installing SAPIENTA for local large-batch annotation in docker-compose mode.

SAPIENTA is compatible with any platform that can run Docker and that supports a 64-bit CPU architecture (SAPIENTA does not currently work on Raspberry PI or Android, nor does it run natively on Apple M-series laptops without Rosetta).

## Step 1: Install Docker + Docker Compose

Docker is a free and open source containerisation system (in plain english: it allows the creation of lightweight "virtual" computers that each run their own operating system within a host machine). Docker-compose is an orchestration and configuration layer for docker (in other words it can be used to manage and configure docker containers to allow them to communicate and work together). Both docker and docker-compose can be installed for free from the [Docker website](https://www.docker.com/) - look for installation instructions for your operating system.

## Step 2: Download the SAPIENTA docker-compose configuration files

Create a new folder and save [docker-compose-local.yml](../docker-compose-local.yml) and rename it `docker-compose.yml`.

## Step 3: Create Papers Directory

Create a subdirectory called `papers` next to your docker-compose.yml and place the files that you want to annotate inside it.

## Step 4: Launch supporting services

Use docker-compose to launch grobid and C&C - these are needed by SAPIENTA to convert PDFs and create features for the final model.

```shell
docker-compose up -d grobid candc
```

## Step 4: Annotate your papers

Finally you can launch sapienta - you need to pass in the names of the papers that you wish to annotate. For example if I have created a file named `test.pdf` in the papers folder I would run:

```shell
docker-compose run sapienta papers/test.pdf
```

**NOTE: Due to the way that docker has been configured, papers must be inside the papers directory. You cannot specify a file outside of this path (docker will give an error if you try)**
