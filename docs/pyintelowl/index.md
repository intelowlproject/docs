:fontawesome-brands-github: [PyIntelOwl Repository](https://github.com/intelowlproject/pyintelowl)

# Welcome to PyIntelOwl's documentation!

## Robust Python SDK and Command Line Client for interacting with IntelOwl API.

### Installation

```
pip install pyintelowl
```

### Usage as CLI

```
 pyintelowl
 Usage: pyintelowl [OPTIONS] COMMAND [ARGS]...

 Options:
 -d, --debug  Set log level to DEBUG
 --version    Show the version and exit.
 -h, --help   Show this message and exit.

 Commands:
 analyse                Send new analysis request
 analyzer-healthcheck   Send healthcheck request for an analyzer...
 config                 Set or view config variables
 connector-healthcheck  Send healthcheck request for a connector
 get-analyzer-config    Get current state of `analyzer_config.json` from...
 get-connector-config   Get current state of `connector_config.json` from...
 get-playbook-config    Get current state of `playbook_config.json` from...
 jobs                   Manage Jobs
 tags                   Manage tags
```

#### Configuration:

You can use `set` to set the config variables and `get` to view them.

```
pyintelowl config set -k 4bf03f20add626e7138f4023e4cf52b8 -u "http://localhost:80"
pyintelowl config get
```

#### Hint
The CLI would is well-documented which will help you navigate various commands easily. Invoke `pyintelowl -h` or `pyintelowl <command> -h` to get help.


### Usage as SDK/library

```python
 from pyintelowl import IntelOwl, IntelOwlClientException
 obj = IntelOwl(
    "4bf03f20add626e7138f4023e4cf52b8",
    "http://localhost:80",
    None,
 )
 """
 obj = IntelOwl(
    "<your_api_key>",
    "<your_intelowl_instance_url>",
    "optional<path_to_pem_file>"
    "optional<proxies>"
 )
 """

 try:
    ans = obj.get_analyzer_configs()
    print(ans)
 except IntelOwlClientException as e:
    print("Oh no! Error: ", e)
```

#### Tip

We very much recommend going through the [:class:`pyintelowl.pyintelowl.IntelOwl`](https://github.com/intelowlproject/pyintelowl/blob/master/docs/index.rst#id1) docs.

### Index

```
.. toctree::
   :maxdepth: 2
   :caption: Usage

   pyintelowl
```

```
  .. toctree::
   :maxdepth: 2
   :caption: Development

   tests

```
