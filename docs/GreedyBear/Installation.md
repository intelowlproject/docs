# Installation

## Requirements
For requirements, please refer to [IntelOwl requirements](https://intelowlproject.github.io/docs/IntelOwl/installation/#requirements) which are the same

Note that GreedyBear _needs_ a running instance of ElasticSearch of a T-POT to function. In `docker/env_file`, set the variable `ELASTIC_ENDPOINT` with the URL of your Elasticsearch T-POT.

In the T-POT classic installation, ElasticSearch is not exposed externally. If you want your GB instance to connect to it, you must change this and expose it externally.

To do that, change the main `docker-compose.yml` of the T-POT in the `elasticsearch` section:
```code
    ports:
      - "64298:9200" # instead of "127.0.0.1:64298:9200"
```
Obviously, you should have already configured your T-POT to avoid generic access to ports higher than 64000 (like stated in the [official doc](https://github.com/telekom-security/tpotce/tree/master?tab=readme-ov-file#system-placement))

If you don't have a T-POT, you can make the following changes to make GreeyBear spin up it's own ElasticSearch instance.
(...Care! This option would require enough RAM to run the additional containers. Suggested is >=16GB):

1. In `docker/env_file`, set the variable `ELASTIC_ENDPOINT` to `http://elasticsearch:9200`.
2. Add `:docker/elasticsearch.yml` to the last defined `COMPOSE_FILE` variable or uncomment the `# local development with elasticsearch container` block in `.env` file.


## Installation steps

Start by cloning the project

```bash
# clone the Greedybear project repository
git clone https://github.com/honeynet/GreedyBear
cd GreedyBear/

# construct environment files from templates
cp .env_template .env
cd docker/
cp env_file_template env_file
cp env_file_postgres_template env_file_postgres
```

```bash
# The default deployment leverages the official images of GreedyBear available here: https://hub.docker.com/repository/docker/intelowlproject/greedybear
# start the app
docker-compose up

# now the app is running on http://localhost:80

# shut down the application
docker-compose down
```

_Note:_ To create a superuser run the following:

```bash
docker exec -ti greedybear_uwsgi python3 manage.py createsuperuser
```

The app administrator can enable/disable the extraction of source IPs for specific honeypots from the Django Admin.
This is used for honeypots that are not specifically implemented to extract additional information (so not Log4Pot and Cowrie).

### Environment configuration

In the `env_file`, configure different variables as explained below.

**Required** variable to set:

- `DEFAULT_FROM_EMAIL`: email address used for automated correspondence from the site manager (example: `noreply@mydomain.com`)
- `DEFAULT_EMAIL`: email address used for correspondence with users (example: `info@mydomain.com`)
- `EMAIL_HOST`: the host to use for sending email with SMTP
- `EMAIL_HOST_USER`: username to use for the SMTP server defined in EMAIL_HOST
- `EMAIL_HOST_PASSWORD`: password to use for the SMTP server defined in EMAIL_HOST. This setting is used in conjunction with EMAIL_HOST_USER when authenticating to the SMTP server.
- `EMAIL_PORT`: port to use for the SMTP server defined in EMAIL_HOST.
- `EMAIL_USE_TLS`: whether to use an explicit TLS (secure) connection when talking to the SMTP server, generally used on port 587.
- `EMAIL_USE_SSL`: whether to use an implicit TLS (secure) connection when talking to the SMTP server, generally used on port 465.

**Optional configuration**:

- `SLACK_TOKEN`: Slack token of your Slack application that will be used to send/receive notifications
- `DEFAULT_SLACK_CHANNEL`: ID of the Slack channel you want to post the message to

## ElasticSearch compatibility.
Greedybear leverages a [python client](https://elasticsearch-py.readthedocs.io/en/v8.19.1/) for interacting with ElasticSearch which requires to be at the exact major version of the related T-POT ElasticSearch instance.
This means that there could problems if those versions do not match.

The current version of the client installed is the 8.19.3 which allows to run TPOT version from 22.04.0 to 24.04.1 without any problems (and some later ones...we regularly check T-POT releases but we could miss one or two here.)

If you want to have compatibility with previous versions, you need to change the `elasticsearch8` version [here](https://github.com/intelowlproject/GreedyBear/blob/main/requirements/project-requirements.txt) and [re-build](https://intelowlproject.github.io/docs/GreedyBear/Installation/#rebuilding-the-project-creating-custom-docker-build) locally the project.

## Update and Re-build

### Rebuilding the project / Creating custom docker build

If you make some code changes and you like to rebuild the project, follow these steps:

1. Be sure that your `.env` file has a `COMPOSE_FILE` variable which mounts the `docker/local.override.yml` compose file.
2. `docker-compose build` to build the new docker image.
3. Start the containers with `docker-compose up`.

### Update to the most recent version

To update the project with the most recent available code you have to follow these steps:

```bash
$ cd <your_greedy_bear_directory> # go into the project directory
$ git pull # pull new repository changes
$ docker pull intelowlproject/greedybear:prod # pull new docker images
$ docker-compose down # stop and destroy the currently running GreedyBear containers
$ docker-compose up # restart the GreedyBear application
```
