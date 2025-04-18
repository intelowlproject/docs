# Advanced Usage

This page includes details about some advanced features that Intel Owl provides which can be **optionally** enabled. Namely,

## Organizations and User management

Starting from IntelOwl v4, a new "Organization" section is available on the GUI. This section substitute the previous permission management via Django Admin and aims to provide an easier way to manage users and visibility.

### Multi Tenancy

Thanks to the "Organization" feature, IntelOwl can be used by multiple SOCs, companies, etc...very easily.
Right now it works very simply: only users in the same organization can see analysis of one another. An user can belong to an organization only.

#### Manage organizations

You can create a new organization by going to the "Organization" section, available under the Dropdown menu you cand find under the username.

Once you create an organization, you are the unique "Owner" of that organization. So you are the only one who can delete the organization and promote/demote/kick users.
Another role, which is called "Admin", can be set to a user (via the Django Admin interface only for now).
Owners and admins share the following powers: they can manage invitations and the organization's plugin configuration.

#### Accept Invites

Once an invite has sent, the invited user has to login, go to the "Organization" section and accept the invite there. Afterwards the Administrator will be able to see the user in his "Organization" section.

![img.png](./static/accept_invite.png)

#### Plugins Params and Secrets

From IntelOwl v4.1.0, Plugin Parameters and Secrets can be defined at the organization level, in the dedicated section.
This allows to share configurations between users of the same org while allowing complete multi-tenancy of the application.
Only Owners and Admins of the organization can set, change and delete them.

#### Disable Plugins at Org level

The org admin can disable a specific plugin for all the users in a specific org.
To do that, Org Admins needs to go in the "Plugins" section and click the button "Enabled for organization" of the plugin that they want to disable.

![img.png](./static/disable_org.png)

### Registration

Since IntelOwl v4.2.0 we added a Registration Page that can be used to manage Registration requests when providing IntelOwl as a Service.

After a user registration has been made, an email is sent to the user to verify their email address. If necessary, there are buttons on the login page to resend the verification email and to reset the password.

Once the user has verified their email, they would be manually vetted before being allowed to use the IntelOwl platform. The registration requests would be handled in the Django Admin page by admins.
If you have IntelOwl deployed on an AWS instance with an IAM role you can use the [SES](/Advanced-Usage.md#ses) service.

To have the "Registration" page to work correctly, you must configure some variables before starting IntelOwl. See [Optional Environment Configuration](https://intelowlproject.github.io/docs/IntelOwl/installation/#other-optional-configuration-to-enable-specific-services-features)

In a development environment the emails that would be sent are written to the standard output.

## Optional Analyzers

Some analyzers which run in their own Docker containers are kept disabled by default. They are disabled by default to prevent accidentally starting too many containers and making your computer unresponsive.

<style>
table, th, td {
  padding: 5px;
  border: 1px solid black;
  border-collapse: collapse;
}
</style>
<table style="width:100%">
  <tr>
    <th>Name</th>
    <th>Analyzers</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>Malware Tools Analyzers</td>
    <td>
      <ul>
      <li><code>PEframe_Scan</code></li>
      <li><code>Capa_Info</code></li>
      <li><code>Floss</code></li>
      <li><code>Strings_Info</code></li>
      <li><code>ClamAV</code></li>
      <li><code>APKiD</code></li>
      <li><code>Droidlysis</code></li>
      <li><code>MobSF</code></li>
      <li><code>APK_Artifacts</code></li>
      <li><code>BoxJS</code></li>
      <li><code>GoReSym</code></li>
      <li><code>Qiling_Windows</code>,
      <code>Qiling_Windows_Shellcode</code>,
      <code>Qiling_Linux</code>,
      <code>Qiling_Linux_Shellcode</code></li>
     </ul>
    </td>
    <td>
    <ul>
      <li>PEFrame performs static analysis on Portable Executable malware and malicious MS Office documents</li>
      <li>CAPA detects capabilities in executable files</li>
      <li>FLOSS automatically deobfuscate strings from malware binaries</li>
      <li>String_Info_Classic extracts human-readable strings where as ML version of it ranks them</li>
      <li>ClamAV antivirus engine scans files for trojans, viruses, malwares using a multi-threaded daemon</li>
      <li>APKiD identifies many compilers, packers, obfuscators, and other weird stuff from an APK or DEX file.</li>
      <li>Droidlysis is a pre-analysis tool for Android apps</li>
      <li>MobSF is a static analysis tool that can find insecure code patterns in your Android and iOS source code</li>
      <li>APK_Artifacts is a tool that does APK strings analysis. Useful for first analysis.</li>
      <li>Box-JS is a tool for studying JavaScript malware</li>
      <li>GoReSym is a Go symbol parser that extracts program metadata, function metadata , filename and line number metadata, and embedded structures and types.</li>
      <li>Qiling is a tool for emulating the execution of a binary file or a shellcode.
     It requires the configuration of its rootfs, and the optional configuration of profiles.
     The rootfs can be copied from the <a href="https://github.com/qilingframework/qiling/tree/master/examples/rootfs"> Qiling project</a>: please remember that Windows dll <b> must</b> be manually added for license reasons.
     Qiling provides a <a href="https://github.com/qilingframework/qiling/blob/master/examples/scripts/dllscollector.bat"> DllCollector</a> to retrieve dlls from your licensed Windows. 
     <a href="https://docs.qiling.io/en/latest/profile/"> Profiles </a> must be placed in the <code>profiles</code> subfolder
     </li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>TOR Analyzers</td>
    <td><code>Onionscan</code></td>
    <td>Scans TOR .onion domains for privacy leaks and information disclosures.</td>
  </tr>
  <tr>
    <td>CyberChef</td>
    <td><code>CyberChef</code></td>
    <td>Run a transformation on a <a href="https://github.com/gchq/CyberChef-server">CyberChef server</a> using pre-defined or custom recipes(rules that describe how the input has to be transformed). Check further instructions <a href="#cyberchef">here</a></td>
  </tr>
    <tr>
    <td>PCAP Analyzers</td>
    <td><code>Suricata</code></td>
    <td>You can upload a PCAP to have it analyzed by Suricata with the open Ruleset. The result will provide a list of the triggered signatures plus a more detailed report with all the raw data generated by Suricata. You can also add your own rules (See paragraph "Analyzers with special configuration"). The installation is optimized for scaling so the execution time is really fast.</td>
  </tr>
  <tr>
    <td>PhoneInfoga</td>
    <td><code>PhoneInfoga_scan</code></td>
    <td><a href="https://github.com/sundowndev/phoneinfoga/tree/master">PhoneInfoga</a> is one of the most advanced tools to scan international phone numbers. It allows you to first gather basic information such as country, area, carrier and line type, then use various techniques to try to find the VoIP provider or identify the owner. It works with a collection of scanners that must be configured in order for the tool to be effective. PhoneInfoga doesn't automate everything, it's just there to help investigating on phone numbers. <a href="#phoneinfoga">here</a></td>
  </tr>
  <tr>
    <td>Phishing Analyzers</td>
    <td>
      <ul>
        <li><code>Phishing_Extractor</code></li>
        <li><code>Phishing_Form_Compiler</code></li>
      </ul>
    </td>
    <td>This framework tries to render a potential phishing page and extract useful information from it. Also, if the page contains a form, it tries to submit the form using fake data. The goal is to extract IOCs and check whether the page is real phishing or not.</td>
  </tr>
  <tr>
    <td>Thug (AMD64 only)</td>
    <td>
      <ul>
        <li><code>Thug_URL_Info</code></li>
        <li><code>Thug_HTML_Info</code></li>
      </ul>
    </td>
    <td>Python low-interaction honeyclient. Thug performs hybrid dynamic/static analysis on a URL or HTML page.</td>
  </tr>
  <tr>
    <td>Nuclei analyzer</td>
    <td>
      <ul>
        <li><code>Nuclei</code></li>
      </ul>
    </td>
    <td>Nuclei is a fast, customizable vulnerability scanner that leverages YAML-based templates to detect, rank, and address security flaws. It operates using structured templates that define specific security checks.</td>
  </tr>
</table>

To enable all the optional analyzers you can add the option `--all_analyzers` when starting the project. Example:

```bash
./start prod up --all_analyzers
```

Otherwise you can enable just one of the cited integration by using the related option. Example:

```bash
./start prod up --tor_analyzers
```

## Customize analyzer execution

Some analyzers provide the chance to customize the performed analysis based on parameters that are different for each analyzer.

##### from the GUI

You can click on "**Runtime Configuration**" ![img.png](./static/runtime_config.png) button in the "Scan" page and add the runtime configuration in the form of a dictionary.
Example:

```javascript
"VirusTotal_v3_File": {
    "force_active_scan_if_old": true
}
```

##### from [Pyintelowl](https://github.com/intelowlproject/pyintelowl)

While using `send_observable_analysis_request` or `send_file_analysis_request` endpoints, you can pass the parameter `runtime_configuration` with the optional values.
Example:

```python
runtime_configuration = {
    "Doc_Info": {
        "additional_passwords_to_check": ["passwd", "2020"]
    }
}
pyintelowl_client.send_file_analysis_request(..., runtime_configuration=runtime_configuration)
```

#### PhoneInfoga

PhoneInfoga provides several [Scanners](https://sundowndev.github.io/phoneinfoga/getting-started/scanners/) to extract as much information as possible from a given phone number. Those scanners may require authentication, so they are automatically skipped when no authentication credentials are found.

By default the scanner used is `local`.
Go through this [guide](https://sundowndev.github.io/phoneinfoga/getting-started/scanners/) to initiate other required API keys related to this analyzer.

#### CyberChef

You can either use pre-defined recipes or create your own as
explained [here](https://github.com/gchq/CyberChef-server#features).

To use a pre-defined recipe, set the `predefined_recipe_name` argument to the name of the recipe as
defined [here](#pre-defined-recipes). Else, leave the `predefined_recipe_name` argument empty and set
the `custom_recipe` argument to the contents of
the [recipe](https://github.com/gchq/CyberChef-server#example-one-operation-non-default-arguments-by-name) you want to
use.

Additionally, you can also (optionally) set the `output_type` argument.

##### Pre-defined recipes

- "to decimal": `[{"op": "To Decimal", "args": ["Space", False]}]`

#### Phishing Analyzers
The framework aims to be extandable and provides two different playbooks connected through a pivot.
The first playbook, named `PhishingExtractor`, is in charge of extracting useful information from the web page rendered with Selenium-based browser.
The second playbook is called `PhishingAnalysis` and its main purposes are to extract useful insights on the page itself
and to try to submit forms with fake data to extract other IOCs.

[XPath](https://www.w3schools.com/xml/xpath_intro.asp) syntax is used to find elements in the page. These selectors are customizable via the plugin's config page.
The parameter `xpath_form_selector` controls how the form is retrieved from the page and `xpath_js_selector` is used to search
for JavaScript inside the page.

A mapping is used in order to compile the page with fake data. This is due to the fact that most input tags of type "text"
do not have a specific role in the page, so there must be some degree of approximation.
This behaviour is controlled through `*-mapping` parameters. They are a list that must contain the input tag's name to
compile with fake data.

Here is an example of what a phishing investigation looks like started from `PhishingExtractor` playbook: 
![img.png](./static/phishing_analysis.png)

##### Infrastructure diagram
To better understand how this integration works, here is a diagram showing how the components are arranged (at container level) and how they communicate to reach target website.
![img.png](./static/intel_owl_phishing_analyzers.png)

## Analyzers with special configuration

Some analyzers could require a special configuration:

- `GoogleWebRisk`: this analyzer needs a service account key with the Google Cloud credentials to work properly.
  You should follow the [official guide](https://cloud.google.com/web-risk/docs/quickstart) for creating the key.
  Then you can populate the secret `service_account_json` for that analyzer with the JSON of the service account file.

- `ClamAV`: this Docker-based analyzer uses `clamd` daemon as its scanner and is communicating with `clamdscan` utility to scan files. The daemon requires 2 different configuration files: `clamd.conf`(daemon's config) and `freshclam.conf` (virus database updater's config). These files are mounted as docker volumes in `/integrations/malware_tools_analyzers/clamav` and hence, can be edited by the user as per needs, without restarting the application. Moreover ClamAV is integrated with unofficial open source signatures extracted with [Fangfrisch](https://github.com/rseichter/fangfrisch). The configuration file `fangfrisch.conf` is mounted in the same directory and can be customized on your wish. For instance, you should change it if you want to integrate open source signatures from [SecuriteInfo](https://www.securiteinfo.com/)

- `Suricata`: you can customize the behavior of Suricata:

  - `/integrations/pcap_analyzers/config/suricata/rules`: here there are Suricata rules. You can change the `custom.rules` files to add your own rules at any time. Once you made this change, you need to either restart IntelOwl or (this is faster) run a new analysis with the Suricata analyzer and set the parameter `reload_rules` to `true`.
  - `/integrations/pcap_analyzers/config/suricata/etc`: here there are Suricata configuration files. Change it based on your wish. Restart IntelOwl to see the changes applied.

- `Yara`:
  - You can customize both the `repositories` parameter and `private_repositories` secret to download and use different rules from the default that IntelOwl currently support.
    - The `repositories` values is what will be used to actually run the analysis: if you have added private repositories, remember to add the url in `repositories` too!
  - You can add local rules inside the directory at `/opt/deploy/files_required/yara/YOUR_USERNAME/custom_rules/`. Please remember that these rules are not synced in a cluster deploy: for this reason is advised to upload them on GitHub and use the `repositories` or `private_repositories` attributes.

- `NERD` :
  - The `nerd_analysis` parameter allows you to customize the level of detail in the analysis response. Available options are:
    - `basic` (default): Provides a simplified response from the database.
    - `full`: Includes all available information about the IP from the database.
    - `fmp`: Returns only the FMP (Future Misbehavior Probability) score.
    - `rep`: Returns only the reputation score of the IP.
- `urlDNA.io`:
  - The `UrlDNA_New_Scan` analyzer offers optional configurations that can be adjusted to achieve more accurate results. Full documentation of these settings is available on the [urlDNA.io API](https://urldna.io/api) page.
    - `device`: Specifies the device used for the scan. Options are `DESKTOP` or `MOBILE`.
    - `user_agent`: Defines the browser user agent string used during the scan.
    - `viewport_width`: Sets the viewport width for the scan.
    - `viewport_height`: Sets the viewport height for the scan.
    - `waiting_time`: Determines the waiting time for the page to load during the scan (in seconds).
    - `private_scan`: When set to `true`, the scan results will not be shared with other `urlDNA.io` users.
    - `scanned_from`: Allows selecting the country of origin for the scan using a two-letter country code (ISO 3166-1 alpha-2). This feature is available only to `urlDNA.io` Premium Users.
- `MobSF_Service`: 
  - The `MobSF_Service` analyzer offers various configurable parameters to optimize the automated scanning of the application as per one's requirement.
    - `enable_dynamic_analysis`: Set to `True` to enable dynamic analysis though this will increase the scan time.
    - `timeout`: Request timeout for each API call, configure as per your need. Default value is 30 seconds.
    - `default_hooks`: Default hooks to pass to mobsf e.g root_bypass, ssl_pinning_bypass, etc.
    - `auxiliary_hooks`: Auxiliary frida hooks to pass to mobsf.
    - `frida_code`: Custom Frida code to be executed by mobsf
    - `activity_duration`: Wait time period for mobsf to collect sufficient info from dynamic activities such as results from`frida_code` before generating report. Default value is 60 seconds. Configure as per your requirements.
    
## Notifications

Since v4, IntelOwl integrated the notification system from the `certego_saas` package, allowing the admins to create notification that every user will be able to see.

The user would find the Notifications button on the top right of the page:

<img style="border: 0.2px solid black" width=220 height=210 src="https://raw.githubusercontent.com/intelowlproject/docs/main/docs/IntelOwl/static/notifications.png">

There the user can read notifications provided by either the administrators or the IntelOwl Maintainers.

As an Admin, if you want to add a notification to have it sent to all the users, you have to login to the Django Admin interface, go to the "Notifications" section and add it there.
While adding a new notification, in the `body` section it is possible to even use HTML syntax, allowing to embed images, links, etc;
in the `app_name field`, please remember to use `intelowl` as the app name.

Everytime a new release is installed, once the backend goes up it will automatically create a new notification,
having as content the latest changes described in the [CHANGELOG.md](https://github.com/intelowlproject/IntelOwl/blob/master/.github/CHANGELOG.md),
allowing the users to keep track of the changes inside intelowl itself.
