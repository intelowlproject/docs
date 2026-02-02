# Usage

## Feeds API

GreedyBear is created with the aim to collect the information from the TPOTs and generate some actionable feeds, so that they can be easily accessible and act as valuable information to prevent and detect attacks.

The feeds are reachable through the following URL:

```
https://<greedybear_site>/api/feeds/<feed_type>/<attack_type>/<prioritize>.<format>?<flags>
```

The available feed_type are:

- `<honeypot_name>`: attacks detected from a specific type of honeypot; for example `cowrie`
- `all`: get all types at once

The available attack_type are:

- `scanner`: IP addresses captured by the honeypots while performing attacks
- `payload_request`: IP addresses and domains extracted from payloads that would have been executed after a speficic attack would have been successful. This will currently only return requests recorded by the Cowrie honeypot. 
- `all`: get all types at once

The available prioritization mechanisms are:

- `recent`: most recent IOCs seen in the last 3 days
- `persistent`: these IOCs are the ones that were seen regularly by the honeypots. This feeds will start empty once no prior data was collected and will become bigger over time.
- `likely_to_recur`: these IOCs are most likely to hit the honeypots again during the next day
- `most_expected_hits`: these IOCs are expected to be responsible for the most hits during the next day

The available formats are:

- `txt`: plain text (just one line for each IOC)
- `csv`: CSV-like file (just one line for each IOC)
- `json`: JSON file with additional information regarding the IOCs

The available flags are: 

- `include_mass_scanners`: if set, IOCs that are known mass scanners will be included in the result
- `include_tor_exit_nodes`: if set, IOCs that are known tor exit nodes will be included in the result

The `json` result includes two predictive scores:

- `recurrence_probability` (0.0-1.0): Indicates the likelihood that an IOC will reappear within the next 24 hours. Higher values suggest greater persistence of the threat.
- `expected_interactions` (0+): Estimates the number of honeypot interactions anticipated from the IOC in the next 24 hours, indicating potential activity level.

These predictions are based on historical interaction patterns and are updated once a day, shortly after midnight UTC. They are the foundation of the `likely_to_recur` and `most_expected_hits` prioritization mechanisms.

Check the [API specification](https://intelowlproject.github.io/docs/GreedyBear/Api-docs/#docs.Submodules.GreedyBear.api.views.feeds.feeds_advanced) or the to get all the details about how to use the available APIs.

## Advanced Feeds API
_Available from version >= 1.4.0_

For authenticated users, GreedyBear offers an additional API endpoint that provides similar functionality to the Feeds API but with enhanced customization options.
```
https://<greedybear_site>/api/feeds/advanced/?<query_params>
```

The available query parameters are:

- `feed_type`: see [Feeds API](#feeds)
- `attack_type`: see [Feeds API](#feeds)
- `max_age`: Maximum number of days since last occurrence. (default: 3)
- `min_days_seen`: Minimum number of days on which an IOC must have been seen. (default: 1)
- `include_reputation`: `;`-separated list of reputation values to include, e.g. `known attacker` or `known attacker;` to include IOCs without reputation. (default: include all)
- `exclude_reputation`: `;`-separated list of reputation values to exclude, e.g. `mass scanner` or `mass scanner;bot, crawler`. (default: exclude none)
- `feed_size`: Number of IOC items to return. (default: 5000)
- `ordering`: Field to order results by, with optional `-` prefix for descending. (default: `-last_seen`)
- `verbose`: `true` to include IOC properties that contain a lot of data, e.g. the list of days it was seen. (default: `false`)
- `paginate`: `true` to paginate results. This forces the json format. (default: `false`)
- `format_`: see [Feeds API](#feeds) (default: `json`)

Check the [API specification](https://intelowlproject.github.io/docs/GreedyBear/Api-docs/) or the to get all the details about how to use the available APIs.

This "Advanced Feeds" API is protected through authentication. Please reach out [Matteo Lodi](https://twitter.com/matte_lodi) or another member of [The Honeynet Project](https://twitter.com/ProjectHoneynet) if you are interested in gain access to this API.

### ASN Aggregated Feeds API
_Available from version >= 3.0.0_

For authenticated users, GreedyBear offers an API endpoint that aggregates IOC data by ASN (Autonomous System Number).
```
https://<greedybear_site>/api/feeds/asn/?<query_params>
```

### Query Parameters
- `feed_type` (optional): See [Feeds API](#feeds) for valid feed types. Default: `all`.
- `attack_type` (optional): See [Feeds API](#feeds) for valid attack types. Default: `all`.
- `max_age` (optional): Maximum age of IOCs in days. Default: 3.
- `min_days_seen` (optional): Minimum days an IOC must have been observed. Default: 1.
- `exclude_reputation` (optional): `;`-separated reputations to exclude (e.g., `mass scanner`). Default: none.
- `ordering` (optional): Aggregation ordering field (e.g., `total_attack_count`, `asn`). Default: `-ioc_count`.
- `asn` (optional): Filter results to a specific ASN.

### Responses
- Response (200): JSON array of ASN aggregation objects. Each object containing:

  - `asn` (int): ASN number.
  - `ioc_count` (int): Number of IOCs for this ASN.
  - `total_attack_count` (int): Sum of attack_count for all IOCs.
  - `total_interaction_count` (int): Sum of interaction_count for all IOCs.
  - `total_login_attempts` (int): Sum of login_attempts for all IOCs.
  - `honeypots` (list[str]): Sorted list of unique honeypots that observed these IOCs.
  - `expected_ioc_count` (float): Sum of `recurrence_probability` for all IOCs, rounded to 4 decimals.
  - `expected_interactions` (float): Sum of `expected_interactions` for all IOCs, rounded to 4 decimals.
  - `first_seen` (datetime): Earliest `first_seen` timestamp among IOCs.
  - `last_seen` (datetime): Latest `last_seen` timestamp among IOCs.

- Response (400): Bad Request - Missing or invalid query parameter.

Check the [API specification](https://intelowlproject.github.io/docs/GreedyBear/Api-docs/) or the to get all the details about how to use the available APIs.

This "ASN Aggregated Feeds" API is protected through authentication. Please reach out [Matteo Lodi](https://twitter.com/matte_lodi) or another member of [The Honeynet Project](https://twitter.com/ProjectHoneynet) if you are interested in gaining access to this API.


## Enrichment API

GreedyBear provides an easy-to-query API to get the information available in GB regarding the queried observable (domain or IP address).

```
https://<greedybear_site>/api/enrichment?query=<observable>
```

This "Enrichment" API is protected through authentication. Please reach out [Matteo Lodi](https://twitter.com/matte_lodi) or another member of [The Honeynet Project](https://twitter.com/ProjectHoneynet) if you are interested in gain access to this API.

If you would like to leverage this API without the need of writing even a line of code and together with a lot of other awesome tools, consider using [IntelOwl](https://github.com/intelowlproject/IntelOwl).


## Cowrie Session API
_Available from version >= 2.1.0_

For authenticated users, GreedyBear offers an API to retrieve session data from the [Cowrie](https://github.com/cowrie/cowrie) honeypot including command sequences, credentials, and session details. Queries can be performed using either an IP address to find all sessions from that source, or a SHA-256 hash to find sessions containing a specific command sequence.

You can query this API endpoint using the following URL:
```
https://<greedybear_site>/api/cowrie_session?query=<observable>
```

### Authentication
This API is protected through authentication. Please reach out [Matteo Lodi](https://twitter.com/matte_lodi) or another member of [The Honeynet Project](https://twitter.com/ProjectHoneynet) if you are interested in gain access to this API on the [Honeynet instance](https://greedybear.honeynet.org/) of GreedyBear.

### Query Parameters
- *query* (required): The search term, can be either an IP address or the SHA-256 hash of a command sequence. When generating a SHA-256 hash to query a multi-line command sequence, ensure you join all command lines with a newline character (`\n`) before calculating the hash. This matches our internal hashing method which uses Python's `"\n".join(sequence)` function.
- *include_similar* (optional): When `true`, the result is expanded to include all sessions that executed command sequences belonging to the same cluster(s) as command sequences found in the initial query result. Requires CLUSTER_COWRIE_COMMAND_SEQUENCES enabled iin the `env_file`. 
- *include_credentials* (optional): When `true`, the response includes all credentials used across matching Cowrie sessions. Credentials are delivered in the `username | password` format.
- *include_session_data* (optional): When `true`, the response includes detailed information about matching Cowrie sessions.

### Responses
- Response (200): JSON object containing:

  - query (str): The original query parameter
  - commands (list[str]): Unique command sequences (newline-delimited strings)
  - sources (list[str]): Unique source IP addresses
  - credentials (list[str], optional): Unique credentials if include_credentials=true
  - sessions (list[object], optional): Session details if include_session_data=true

    - time (datetime): Session start time
    - duration (float): Session duration in seconds
    - source (str): Source IP address
    - interactions (int): Number of interactions in session
    - credentials (list[str]): Credentials used in this session
    - commands (str): Command sequence executed (newline-delimited)

- Response (400): Bad Request - Missing or invalid query parameter
- Response (404): Not Found - No matching sessions found


### Examples

#### Example 1: Query an IP Address with Credentials
**Request:**
```
GET /api/cowrie_session?query=60.188.124.194&include_credentials=true
```

**Response:**
```json
{
  "license": "https://github.com/honeynet/GreedyBear/blob/main/FEEDS_LICENSE.md",
  "query": "60.188.124.194",
  "commands": [
    "uname -a"
  ],
  "sources": [
    "60.188.124.194"
  ],
  "credentials": [
    "ADMIN | #K2_7f@c048Z",
    "albert | admin",
    //...
    "zccloud | d5EJQLN0nid8B6HXHHxP"
  ]
}
```
#### Example 2: Query a Command Sequence Hash: 
**Request:**
```
GET /api/cowrie_session?query=28ba533b0f3c4df63d6b4a5ead73860697bdf735bb353e4ca928474889eb8a15
```

**Response:**
```json
{
  "query": "28ba533b0f3c4df63d6b4a5ead73860697bdf735bb353e4ca928474889eb8a15",
  "commands": [
    "uname -a"
  ],
  "sources": [
    "60.188.124.194"
  ]
}
```
#### Example 3: Query an IP Address with Similar Sessions: 
**Request:**
```
GET /api/cowrie_session?query=60.188.124.194&include_similar=true
```

**Response:**
```json
{
  "query": "60.188.124.194",
  "commands": [
    "uname -a",
    "uname -s -m"
  ],
  "sources": [
    "60.188.124.194",
    "103.106.104.87",
    "183.204.86.10",
    "221.203.35.59"
  ]
}
```



## User management

### Registration

_WARNING_ This functionality has been removed from the v.1.5.0 onwards because it was not used. In case you need it, please ask it and we re-add it to the project.

Since Greedybear v1.1.0 we added a Registration Page that can be used to manage Registration requests when providing GreedyBear as a Service.

After an user registration, an email is sent to the user to verify their email address. If necessary, there are buttons on the login page to resend the verification email and to reset the password.

Once the user has verified their email, they would be manually vetted before being allowed to use the GreedyBear platform. The registration requests would be handled in the Django Admin page by admins.
If you have GreedyBear deployed on an AWS instance you can use the SES service.

In a development environment the emails that would be sent are written to the standard output.


### Amazon SES

If you like, you could use Amazon SES for sending automated emails.

First, you need to configure the environment variable `AWS_SES` to `True` to enable it.
Then you have to add some credentials for AWS: if you have GreedyBear deployed on the AWS infrastructure, you can use IAM credentials:
to allow that just set `AWS_IAM_ACCESS` to `True`. If that is not the case, you have to set both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

Additionally, if you are not using the default AWS region of us-east-1, you need to specify your `AWS_REGION`.
You can customize the AWS Region location of you services by changing the environment variable `AWS_REGION`. Default is `eu-central-1`.