# Advanced Configuration

This page includes details about some advanced features that Intel Owl provides which can be **optionally** configured by the administrator.

## ElasticSearch

_Available for version > 6.1.0_

Right now only ElasticSearch v8 is supported.

### Configuration
In the `env_file_app_template`, you'd see various elasticsearch related environment variables. The user should spin their own Elastic Search instance and configure these variables.

* ELASTICSEARCH_DSL_ENABLED: Enable the ElasticSearch integration to perform advanced searches.
* ELASTICSEARCH_DSL_HOST: URL of the Elasticsearch instance.
* ELASTICSEARCH_DSL_PASSWORD: (optional) Password of the "elastic" user. This can be empty in case of external services with credentials in the url.
* ELASTICSEARCH_BI_ENABLED: Use the Business Intelligence feature.
* ELASTICSEARCH_BI_HOST: URL of the Elasticsearch instance for the BI.
* ELASTICSEARCH_BI_INDEX: Base path of the BI index.

In the `env_file_elasticsearch_template` there is a viarable called `ELASTICSEARCH_PASSWORD`. This name is forced by elastic to set the password into the container.

#### Example Configuration

* Use external instance: In this case it's enough to set the `ELASTICSEARCH_DSL_ENABLED` to `True` and `ELASTICSEARCH_DSL_HOST` with the URL of the external instance.
* Use docker instance:
   * Before starting IntelOwl move inside `docker` folder.
   * `cp env_file_elasticsearch_template env_file_elasticsearch`
   * Populate the var `ELASTICSEARCH_PASSWORD` inside the file `env_file_elasticsearch`.
   * Populate the var `ELASTICSEARCH_DSL_PASSWORD` in the file `env_file_app` with the same value of `ELASTICSEARCH_PASSWORD`. Populate also `ELASTICSEARCH_DSL_HOST` with https://elasticsearch:9200.
   * Start the project with `--elastic` in this way a container based Elasticsearch instance will start.

### Data Search

Thanks to [django-elasticsearch-dsl](https://django-elasticsearch-dsl.readthedocs.io/en/latest/about.html) Job results are indexed into elasticsearch. The `save` and `delete` operations are auto-synced so you always have the latest data in ES.

With [elasticsearch-py](https://elasticsearch-py.readthedocs.io/en/8.x/index.html) the AnalyzerReport, ConnectorReport and PivotReport objects are indexed into elasticsearch. In this way is possible to search data inside the report fields and many other via the UI. Each time IntelOwl is restarted the index template is updated and the every 5 minutes a task insert the reports in ElasticSearch. 

### Business Intelligence

IntelOwl stores data that can be used for Business Intelligence purpose.
Since plugin reports are deleted periodically, this feature allows to save indefinitely small amount of data to keep track of how analyzers perform and user usage.
At the moment, the following information are sent to elastic:

- application name
- timestamp
- username
- configuration used
- process_time
- status
- end_time
- parameters

Documents are saved in the `ELEASTICSEARCH_BI_INDEX-%YEAR-%MONTH`, allowing to manage the retention accordingly.
To activate this feature, it is necessary to set `ELASTICSEARCH_BI_ENABLED` to `True` in the `env_file_app` and
`ELASTICSEARCH_BI_HOST` to `elasticsearch:9200`
or your elasticsearch server.

An [index template](https://github.com/intelowlproject/IntelOwl/blob/master/configuration/elastic_search_mappings/intel_owl_bi.json) is created after the first bulk submission of reports.

## Authentication options

IntelOwl provides support for some of the most common authentication methods:

- [Google Oauth2](#google-oauth2)
- [LDAP](#ldap)
- [RADIUS](#radius-authentication)

#### Google OAuth2

The first step is to create a [Google Cloud Platform](https://cloud.google.com/resource-manager/docs/creating-managing-projects) project, and then [create OAuth credentials for it](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id).

It is important to add the correct callback in the "Authorized redirect URIs" section to allow the application to redirect properly after the successful login. Add this:

```url
http://<localhost|yourowndomain>/api/auth/google-callback
```

After that, specify the client ID and secret as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables and restart IntelOwl to see the applied changes.

<div class="admonition note">
<p class="admonition-title">Note</p>
While configuring Google Auth2 you can choose either to enable access to the all users with a Google Account ("External" mode) or to enable access to only the users of your organization ("Internal" mode).
<a href="https://support.google.com/cloud/answer/10311615#user-type&zippy=%2Cinternal%2Cexternal" target="_blank">Reference</a>
</div>

#### LDAP

IntelOwl leverages [Django-auth-ldap](https://github.com/django-auth-ldap/django-auth-ldap) to perform authentication via LDAP.

How to configure and enable LDAP on Intel Owl?

1. Change the values with your LDAP configuration inside `configuration/ldap_config.py`. This file is mounted as a docker volume, so you won't need to rebuild the image.

<div class="admonition note">
<p class="admonition-title">Note</p>
For more details on how to configure this file, check the <a href="https://django-auth-ldap.readthedocs.io/en/latest/" target="_blank">official documentation</a> of the django-auth-ldap library.
</div>

2. Once you have done that, you have to set the environment variable `LDAP_ENABLED` as `True` in the environment configuration file `env_file_app`.
   Finally, you can restart the application with `docker-compose up`

#### RADIUS Authentication

IntelOwl leverages [Django-radius](https://github.com/robgolding/django-radius) to perform authentication
via RADIUS server.

How to configure and enable RADIUS authentication on Intel Owl?

1. Change the values with your RADIUS auth configuration inside `configuration/radius_config.py`. This file is mounted as a
   docker volume, so you won't need to rebuild the image.

<div class="admonition note">
<p class="admonition-title">Note</p>
For more details on how to configure this file, check the <a href="https://github.com/robgolding/django-radius" target="_blank">official documentation</a> of the django-radius library.
</div>

2. Once you have done that, you have to set the environment variable `RADIUS_AUTH_ENABLED` as `True` in the environment
   configuration file `env_file_app`. Finally, you can restart the application with `docker-compose up`

## OpenCTI

Like many other integrations that we have, we have an [Analyzer](https://intelowlproject.github.io/docs/IntelOwl/usage/#analyzers) and a [Connector](https://intelowlproject.github.io/docs/IntelOwl/usage/#connectors) for the [OpenCTI](<[OpenCTI](https://github.com/OpenCTI-Platform/opencti)>) platform.

This allows the users to leverage these 2 popular open source projects and frameworks together.

So why we have a section here? This is because there are various compatibility problems with the [official PyCTI library](https://github.com/OpenCTI-Platform/client-python/).

We found out (see issues in [IntelOwl](https://github.com/intelowlproject/IntelOwl/issues/1730) and [PyCTI](https://github.com/OpenCTI-Platform/client-python/issues/287)) that, most of the times, it is required that the OpenCTI version of the server you are using and the pycti version installed in IntelOwl **must** match perfectly.

Because of that, we decided to provide to the users the chance to customize the version of PyCTI installed in IntelOwl based on the OpenCTI version that they are using.

To do that, you would need to leverage the option `--pycti-version` provided by the `./start` helper:

- check the default version that would be installed by checking the description of the option `--pycti-version` with `./start -h`
- if the default version is different from your OpenCTI server version, you need to rebuild the IntelOwl Image with `./start test build --pycti-version <your_version>`
- then restart the project `./start test up -- --build`
- enjoy

## Cloud Support

### AWS support

We have support for several AWS services.

You can customize the AWS Region location of you services by changing the environment variable `AWS_REGION`. Default is `eu-central-1`

You have to add some credentials for AWS: if you have IntelOwl deployed on the AWS infrastructure, you can use IAM credentials:
to allow that just set `AWS_IAM_ACCESS` to `True`. If that is not the case, you have to set both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

#### S3

If you prefer to use S3 to store the analyzed samples, instead of the local storage, you can do it.

First, you need to configure the environment variable `LOCAL_STORAGE` to `False` to enable it and set `AWS_STORAGE_BUCKET_NAME` to the AWS bucket you want to use.

Then you need to configure permission access to the chosen S3 bucket.

#### Message Broker

IntelOwl at the moment supports 3 different message brokers:

- Redis (default)
- RabbitMQ
- Aws SQS

The default broker, if nothing is specified, is `Redis`.

To use `RabbitMQ`, you must use the option `--rabbitmq` when launching IntelOwl with the `./start` script.

To use `AWS SQS`, you must use the option `--sqs` when launching IntelOwl with the `.start` script.
In that case, you should create new FIFO SQS queues in AWS called `intelowl-<environment>-<queue_name>.fifo` and give your instances on AWS the proper permissions to access it.
Moreover, you must populate the `AWS_USER_NUMBER`. This is required to connect in the right way to the selected SQS queues.
Only FIFO queues are supported.

If you want to use a remote message broker (like an `ElasticCache` or `AmazonMQ` instance), you must populate the `BROKER_URL` environment variable.

It is possible to use [task priority](https://docs.celeryq.dev/en/stable/userguide/routing.html#special-routing-options) inside IntelOwl: each User has default priority of 10, and robots users (like the Ingestors) have a priority of 7.  
You can customize these priorities inside Django Admin, in the `Authentication.User Profiles` section.

#### Websockets

`Redis` is used for two different functions:

- message broker
- websockets

For this reason, a `Redis` instance is **mandatory**.
You can personalize IntelOwl in two different way:

- with a local `Redis` instance.

This is the default behaviour.

- With a remote `Redis` instance.

You must use the option `--use-external-redis` when launching IntelOwl with the `.start` script.
Moreover, you need to populate the `WEBSOCKETS_URL` environment variable. If you are using `Redis` as a message broker too, remember to populate the `BROKER_URL` environment variable

#### RDS

If you like, you could use AWS RDS instead of PostgreSQL for your database. In that case, you should change the database required options accordingly: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` and setup your machine to access the service.

If you have IntelOwl deployed on the AWS infrastructure, you can use IAM credentials to access the Postgres DB.
To allow that just set `AWS_RDS_IAM_ROLE` to `True`. In this case `DB_PASSWORD` is not required anymore.

Moreover, to avoid to run PostgreSQL locally, you would need to use the option `--use-external-database` when launching IntelOwl with the `./start` script.

#### SES

If you like, you could use Amazon SES for sending automated emails (password resets / registration requests, etc).

You need to configure the environment variable `AWS_SES` to `True` to enable it.

#### Secrets

You can use the "Secrets Manager" to store your credentials. In this way your secrets would be better protected.

First you need to set the environment variable `AWS_SECRETS` to `True` to enable this mode.

Then, instead of adding the variables to the environment file, you should just add them with the same name on the AWS Secrets Manager and Intel Owl will fetch them transparently.

Beware! Any left environment variable would be prioritized. So, you want to use your secrets in AWS, make sure to have removed the related environment variables locally.

Obviously, you should also have created and managed the permissions in AWS in advance and accordingly to your infrastructure requirements.

#### NFS

You can use a `Network File System` for the shared_files that are downloaded runtime by IntelOwl (for example Yara rules).

To use this feature, you would need to add the address of the remote file system inside the `.env` file,
and you would need to use the option `--nfs` when launching IntelOwl with the `./start` script.

### Google Kubernetes Engine

Right now there is no official support for Kubernetes deployments.

But we have an active community. Please refer to the following blog post for an example on how to deploy IntelOwl on Google Kubernetes Engine:

[Deploying Intel-Owl on GKE](https://mostwanted002.cf/post/intel-owl-gke/) by [Mayank Malik](https://twitter.com/_mostwanted002_).

## Queues

#### Multi Queue

IntelOwl provides an additional [multi-queue.override.yml](https://github.com/intelowlproject/IntelOwl/blob/master/docker/multi-queue.override.yml) compose file allowing IntelOwl users to better scale with the performance of their own architecture.

If you want to leverage it, you should add the option `--multi-queue` when starting the project. Example:

```bash
./start prod up --multi-queue
```

This functionality is not enabled by default because this deployment would start 2 more containers so the resource consumption is higher. We suggest to use this option only when leveraging IntelOwl massively.

#### Queue Customization

It is possible to define new celery workers: each requires the addition of a new container in the docker-compose file, as shown in the `multi-queue.override.yml`.

Moreover IntelOwl requires that the name of the workers are provided in the `docker-compose` file. This is done through the environment variable `CELERY_QUEUES` inside the `uwsgi` container. Each queue must be separated using the character `,`, as shown in the [example](https://github.com/intelowlproject/IntelOwl/blob/master/docker/multi-queue.override.yml#L6).

One can customize what analyzer should use what queue by specifying so in the analyzer entry in the [analyzer_config.json](https://github.com/intelowlproject/IntelOwl/blob/master/configuration/analyzer_config.json) configuration file. If no queue(s) are provided, the `default` queue will be selected.

#### Queue monitoring

IntelOwl provides an additional [flower.override.yml](https://github.com/intelowlproject/IntelOwl/blob/master/docker/flower.override.yml) compose file allowing IntelOwl users to use [Flower](https://flower.readthedocs.io/) features to monitor and manage queues and tasks

If you want to leverage it, you should add the option `--flower` when starting the project. Example:

```bash
./start prod up --flower
```

The flower interface is available at port 5555: to set the credentials for its access, update the environment variables

```bash
FLOWER_USER
FLOWER_PWD
```

or change the `.htpasswd` file that is created in the `docker` directory in the `intelowl_flower` container.

## Chatbot

_Available from version >= 6.7.0_

The optional LLM chatbot (enabled with the `--ollama` flag, see
[installation](./installation.md#chatbot-ollama)) is configured through the following variables, set
like every other secret in `docker/env_file_app`. All have sensible defaults; override them only if
needed.

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | URL of the Ollama runtime. |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Model the agent uses; must support Ollama tool calling (see [Fine-tuning & Prompting](./chatbot_tuning.md)). |
| `CHATBOT_MESSAGE_RETENTION_DAYS` | `90` | Conversations idle for this many days are pruned by a daily task. |
| `CHATBOT_RATE_LIMIT` | `5` | Max messages a user may send per window (REST and WebSocket share the bucket). |
| `CHATBOT_RATE_LIMIT_WINDOW` | `60` | Rate-limit window, in seconds. |
| `CHATBOT_PENDING_ACTION_TTL` | `600` | Lifetime, in seconds, of a previewed-analysis confirmation before it expires. |

**CPU / GPU.** The chatbot runs on CPU by default and the `qwen2.5:3b` default is sized for that. GPU
passthrough is not yet supported (tracked in
[issue #3717](https://github.com/intelowlproject/IntelOwl/issues/3717)). For changing the model, the
context window, or packaging a custom model, see the
[Fine-tuning & Prompting](./chatbot_tuning.md) guide.

## MISP

IntelOwl can optionally deploy a self-hosted [MISP](https://www.misp-project.org/) instance
alongside the main application stack. This is enabled with the `--misp` flag
(see [installation](./installation.md#misp)).

### Configuration

MISP is configured via the environment file `docker/env_file_misp`. A comprehensive template with
all available options is provided at `docker/env_file_misp_template`.

To customize your MISP deployment:

```bash
cd docker
cp env_file_misp_template env_file_misp
# Edit env_file_misp with your preferred values
```

The most important variables are:

| Variable | Default | Purpose |
|---|---|---|
| `ADMIN_EMAIL` | `admin@admin.test` | Login email for the MISP admin user. |
| `ADMIN_PASSWORD` | `admin` | Login password for the MISP admin user. |
| `ADMIN_KEY` | `mispdefaultintelowladminapikeychgme01234` | API key used by IntelOwl's MISP connector/analyzer. Must be exactly 40 characters. |
| `ADMIN_ORG` | `IntelOwl` | Name of the default MISP organization. |
| `BASE_URL` | `https://misp-core` | MISP's canonical URL (see note on GUI access below). |
| `MYSQL_PASSWORD` | `misp_password` | MariaDB password (must match `misp-db` service). |
| `REDIS_PASSWORD` | `misp_redis_password` | Redis password (must match `misp-redis` service). |

The template file (`env_file_misp_template`) includes many more options inherited from the
[official MISP Docker project](https://github.com/MISP/misp-docker), including:

- PHP memory limits and FPM pool configuration
- OIDC, LDAP, and Azure AD authentication
- Proxy and S3 storage settings
- Sync server configuration
- Nginx and FastCGI tuning

### Accessing the MISP Web GUI

By default, the MISP container does **not** expose any ports to the host — it is only reachable
from within the Docker network (i.e., by IntelOwl's backend). This is intentional for security.

If you want to access the MISP web interface from your browser, you need to:

1. **Expose the port.** Add port mapping to the `misp-core` service. You can do this via
   `docker/custom.override.yml` (use with `--custom` flag):

    ```yaml
    services:
      misp-core:
        ports:
          - "8443:443"
    ```

2. **Update the `BASE_URL`.** MISP enforces strict URL matching — it will redirect all requests
   to its configured `BASE_URL`. Change it in `docker/env_file_misp` to match how you access
   it from your browser:

    ```env
    BASE_URL=https://localhost:8443
    ```

    Or, if accessing from another machine on your network:

    ```env
    BASE_URL=https://192.168.1.50:8443
    ```

3. **Restart the MISP containers** to apply the changes.

<div class="admonition note">
<p class="admonition-title">Note</p>
MISP enforces a single, fixed <code>BASE_URL</code> for security reasons (Host Header Injection
protection). You cannot access MISP from multiple different URLs simultaneously. Choose one
canonical URL that matches your deployment.
</div>

<div class="admonition note">
<p class="admonition-title">Note</p>
Changing the <code>BASE_URL</code> does <strong>not</strong> affect IntelOwl's API connectivity.
IntelOwl's MISP connector always connects via the internal Docker hostname
(<code>https://misp-core</code>), regardless of the <code>BASE_URL</code> setting.
</div>

### MISP Modules

The optional MISP container does **not** include the `misp-modules` service (MISP's own enrichment
modules). This is intentional -- IntelOwl already provides its own enrichment pipeline via analyzers,
making MISP modules redundant and saving significant resources (~500MB+ image).

If you need MISP modules for other purposes, you can add the service via `docker/custom.override.yml`:

```yaml
services:
  misp-modules:
    image: ghcr.io/misp/misp-docker/misp-modules:latest
    container_name: intelowl_misp_modules
    hostname: misp-modules
    restart: unless-stopped
    healthcheck:
      test: "/bin/bash -c '</dev/tcp/localhost/6666'"
      interval: 5s
      timeout: 2s
      retries: 3
      start_period: 10s
```


## Manual Usage

The `./start` script essentially acts as a wrapper over Docker Compose, performing additional checks.
IntelOwl can still be started by using the standard `docker compose` command, but all the dependencies have to be manually installed by the user.

### Options

The `--project-directory` and `-p` options are required to run the project.
Default values set by `./start` script are "docker" and "intel_owl", respectively.

The startup is based on [chaining](https://docs.docker.com/compose/multiple-compose-files/merge/) various Docker Compose YAML files using `-f` option.
All Docker Compose files are stored in `docker/` directory of the project.
The default compose file, named `default.yml`, requires configuration for an external database and message broker.
In their absence, the `postgres.override.yml` and `rabbitmq.override.yml` files should be chained to the default one.

The command composed, considering what is said above (using `sudo`), is

```bash
sudo docker compose --project-directory docker -f docker/default.yml -f docker/postgres.override.yml -f docker/rabbitmq.override.yml -p intel_owl up
```

The other most common compose file that can be used is for the testing environment.
The equivalent of running `./start test up` is adding the `test.override.yml` file, resulting in:

```bash
sudo docker compose --project-directory docker -f docker/default.yml -f docker/postgres.override.yml -f docker/rabbitmq.override.yml -f docker/test.override.yml -p intel_owl up
```

All other options available in the `./start` script (`./start -h` to view them) essentially chain other compose file to `docker compose` command with corresponding filenames.

### Optional Analyzer

IntelOwl includes integrations with [some analyzer](https://intelowlproject.github.io/docs/IntelOwl/advanced_usage/#optional-analyzers) that are not enabled by default.
These analyzers, stored under the `integrations/` directory, are packed within Docker Compose files.
The `compose.yml` file has to be chained to include the analyzer.
The additional `compose-test.yml` file has to be chained for testing environment.
