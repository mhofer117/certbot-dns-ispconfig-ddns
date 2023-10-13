# certbot-dns-ispconfig-ddns

[ISPConfig](https://www.ispconfig.org/) DNS Authenticator plugin for [Certbot](https://certbot.eff.org/)
using tokens from the ISPConfig [DDNS module](https://github.com/mhofer117/ispconfig-ddns-module) 

This plugin automates the process of completing a `dns-01` challenge by
creating, and subsequently removing, TXT records.

### Configuration of ISPConfig

In the `DNS -> Dynamic DNS -> Tokens` you need to have a token with the following rights:

- Allowed zones: all DNS zones for which you want to create ssl certificates 
- Allowed record types: `TXT`
- Limit records: `_acme-challenge`

If you want to create certificates for subdomains, they must be included in the Limit records:
`_acme-challenge,_acme-challenge.subdomain1,_acme-challenge.subdomain2`

### Installation
```
pip install certbot-dns-ispconfig-ddns
```

### Usage
#### Credentials file or cli parameters

You can either use cli parameters to pass authentication information to certbot:

```commandline
...
--dns-ispconfig-ddns-endpoint <your-ispconfig-url (e.g. https://server.example.com:8080>
--dns-ispconfig-ddns-token <your-ddns-token>
```

Or to prevent your credentials from showing up in your bash history, you can also create a
credentials-file `ispconfig-ddns.ini` (the name does not matter) with the following content:

```ini
dns_ispconfig_ddns_endpoint=<your-ispconfig-url (e.g. https://server.example.com:8080>
dns_ispconfig_ddns_token=<your-ddns-token>
```

And then instead of using the `--dns-ispconfig-ddns-*` parameters above, you can use

```commandline
...
--dns-ispconfig-ddns-credentials </path/to/your/ispconfig-ddns.ini>
```

You can also mix these usages, though the cli parameters always take precedence over the ini file.



### Examples

To acquire a single certificate for both `example.com` and `*.example.com`:

```commandline
certbot certonly \
    --non-interactive \
    --agree-tos \
    --email <your-email> \
    --preferred-challenges dns \
    --authenticator dns-ispconfig-ddns \
    --dns-ispconfig-ddns-endpoint <https://server.example.com:8080> \
    --dns-ispconfig-ddns-token <your-ddns-token> \
    --dns-ispconfig-ddns-propagation-seconds 60 \
    -d 'example.com' \
    -d '*.example.com'
```
