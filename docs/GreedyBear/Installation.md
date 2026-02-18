# Installation

## Requirements
- Hardware (minimum): 2 CPU, 4 GB RAM (16 GB if using a local Elasticsearch instance), 20 GB Disk
- Operating system: a current version of Ubuntu or Debian (recommended); Fedora Centos RHEL, Alma Linux, Rocky Linux and OpenSUSE _should_ also work
- Software: sudo, git

Note that GreedyBear _needs_ a running instance of Elasticsearch from a T-Pot to function. In `docker/env_file`, set the variable `ELASTIC_ENDPOINT` with the URL of your Elasticsearch T-Pot.

In the T-Pot classic installation, Elasticsearch is not exposed externally. If you want your GreedyBear instance to connect to it, you must change this and expose it externally.

To do that, change the main `docker-compose.yml` of the T-Pot in the `elasticsearch` section:
```code
    ports:
      - "64298:9200" # instead of "127.0.0.1:64298:9200"
```

Obviously, you should have already configured your T-Pot to avoid generic access to ports higher than 64000 (like stated in the [official doc](https://github.com/telekom-security/tpotce/tree/master?tab=readme-ov-file#system-placement))


## Installation

Start by cloning the project:

```bash
# clone the GreedyBear project repository
git clone https://github.com/intelowlproject/GreedyBear
cd GreedyBear/
```

Initialize GreedyBear. This process checks system requirements, installs the required packages, checks out the appropriate git branch, and generates environment files:

```bash
# Production environment with external T-Pot Elasticsearch
./gbctl init --elastic-endpoint http://tpot-host:64298
```


### Configuration

After the initialization has finished, your GreedyBear instance is already runnable. However you should consider checking and filling the `docker/env_file`, which contains all important configuration options for the GreedyBear instance. We recommend to populate at least the Email settings:

- `DEFAULT_FROM_EMAIL`: email address used for automated correspondence from the site manager (example: `noreply@mydomain.com`)
- `DEFAULT_EMAIL`: email address used for correspondence with users (example: `info@mydomain.com`)
- `EMAIL_HOST`: the host to use for sending email with SMTP
- `EMAIL_HOST_USER`: username to use for the SMTP server defined in EMAIL_HOST
- `EMAIL_HOST_PASSWORD`: password to use for the SMTP server defined in EMAIL_HOST. This setting is used in conjunction with EMAIL_HOST_USER when authenticating to the SMTP server.
- `EMAIL_PORT`: port to use for the SMTP server defined in EMAIL_HOST.
- `EMAIL_USE_TLS`: whether to use an explicit TLS (secure) connection when talking to the SMTP server, generally used on port 587.
- `EMAIL_USE_SSL`: whether to use an implicit TLS (secure) connection when talking to the SMTP server, generally used on port 465.

### Monitoring Configuration
To receive messages about errors occurring at the instance, it is also recommended to use one of the monitoring options:

- `SLACK_TOKEN`: Slack token of your Slack application that will be used to send/receive notifications
- `DEFAULT_SLACK_CHANNEL`: ID of the Slack channel you want to post the message to
- `NTFY_URL`: URL of a ntfy topic to receive error alerts

## Start the Application

```bash
# Start all services
./gbctl up
```

Now the app is running on http://localhost:80 . You can always check its status or take a look at the logs:


```bash
# Check the status of relevant containers
./gbctl health
# Check the docker logs
./gbctl logs
# Check the application logs
./gbctl logs app
```

Next, create a Django superuser. The Django superuser can enable/disable the extraction of source IPs for specific honeypots from the Django Admin Interface.

```bash
# Create a Django superuser
./gbctl create-admin
```

To shut down the application, run:
```bash
# Stop all services
./gbctl down
```

## Elasticsearch Compatibility
GreedyBear leverages a [python client](https://elasticsearch-py.readthedocs.io/en/v9.3.0) for interacting with Elasticsearch which requires to be at the exact major version of the related T-Pot Elasticsearch instance.
This means that there could be problems if those versions do not match.

The current version of the client installed is the 9.3.0 which allows running T-Pot version >= 24.04.1 without any problems (we regularly check T-Pot releases but we could miss one or two here).


## Update and Re-build

### Rebuilding the project / Creating custom docker build

If you make some code changes and you like to rebuild the project, make sure that your `.env` file has a `COMPOSE_FILE` variable which mounts the `docker/local.override.yml` compose file. You can also run `./gbctl init --dev` to achieve this. With the `docker/local.override.yml` mounted, run:

```bash
./gbctl build # Build the new docker image
./gbctl up # Start all services
```

### Update to the most recent version

Since GreedyBear version 3.1.0 you can update your instance by running in your GreedyBear directory:
```bash
./gbctl update
```

To update manually you have to follow these steps:

```bash
$ git pull # pull new repository changes
$ docker compose pull # pull new docker images
$ docker compose down # stop and destroy the currently running GreedyBear containers
$ docker compose up # restart the GreedyBear application
```



<div class="admonition warning">
<p class="admonition-title">Note</p>
A bug was introduced in GreedyBear version 2.0.0 and fixed in version 3.0.1. If you are running any version between 2.0.0 and 3.0.0 and pull the latest PostgreSQL Docker container, you will end up with an empty database. To fix this, update GreedyBear to version 3.0.1 or later, and your historic data will be visible again. For further information, please refer to this <a href="https://github.com/intelowlproject/GreedyBear/issues/766">issue</a>. 
</div>
