from typing import Callable

from certbot import errors
from certbot.plugins import dns_common

from certbot_dns_ispconfig_ddns.ispconfig_client import ISPConfigClient

DEFAULT_PROPAGATION_SECONDS = 60


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for ISPConfig

    This Authenticator uses the ISPConfig DDNS modules API
    to fulfill a dns-01 challenge.
    """

    description = ("Obtain certificates using a DNS TXT record for ISPConfig "
                   "domains with DDNS module tokens")

    def __init__(self, *args, **kwargs) -> None:
        super(Authenticator, self).__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(
        cls,
        add: Callable[..., None],
        default_propagation_seconds: int = DEFAULT_PROPAGATION_SECONDS
    ) -> None:
        """
        Add required or optional argument for the cli of certbot.

        :param add: method handling the argument adding to the cli
        :param default_propagation_seconds: the default required propagation
                                            time in seconds
        """

        super(Authenticator, cls).add_parser_arguments(
            add,
            default_propagation_seconds=DEFAULT_PROPAGATION_SECONDS
        )
        add("credentials", help="ISPConfig DDNS credentials INI file.")
        add(
            "endpoint",
            help="ISPConfig endpoint (overwrites credentials file)"
        )
        add("token", help="ISPConfig DDNS token (overwrites credentials file)")

    def more_info(self) -> str:
        """
        Get more information about this plugin.
        This method is used by certbot to show more info about this plugin.

        :return: string with more information about this plugin
        """
        return ("This plugin configures a DNS TXT record to respond to a "
                "dns-01 challenge using the ISPConfig DDNS module API.")

    def _setup_credentials(self):
        # If endpoint and token cli params are provided,
        # we do not need a credentials file
        if self.conf("endpoint") and self.conf("token"):
            return

        self._configure_file('credentials',
                             'ISPConfig DDNS credentials INI file')
        dns_common.validate_file_permissions(self.conf('credentials'))
        self.credentials = self._configure_credentials(
            "credentials",
            "ISPConfig DDNS credentials INI file",
            {
                "endpoint": "URL of the ISPConfig Installation.",
                "token": "The generated DDNS module token.",
            },
        )

    def _perform(
        self, domain: str, validation_name: str, validation: str
    ) -> None:
        """
        Add the TXT record to the provided domain.

        :param domain: the domain being validated
        :param validation_name: the validation record including domain name
        :param validation: the value for the TXT record
        :raise PluginError: if creating the TXT record produces any error
        """
        try:
            self._get_ispconfig_client().set_txt_record(
                validation_name, validation
            )
        except Exception as e:
            raise errors.PluginError(e)

    def _cleanup(
        self, domain: str, validation_name: str, validation: str
    ) -> None:
        """
        Delete the dns record corresponding to this validation.

        :param domain: the domain being validated
        :param validation_name: the validation record including domain name
        :param validation: the value of the TXT record
        :raise PluginError: if removing the TXT record produces any error
        """
        try:
            self._get_ispconfig_client().del_txt_record(
                validation_name, validation
            )
        except Exception as e:
            raise errors.PluginError(e)

    def _get_ispconfig_client(self) -> ISPConfigClient:
        """
        Create a new ISPConfigClient instance with the provided credentials.

        :return: the created ISPConfigClient object
        """
        endpoint = self.conf("endpoint") or self.credentials.conf("endpoint")
        token = self.conf("token") or self.credentials.conf("token")
        return ISPConfigClient(
            endpoint=endpoint,
            token=token
        )
