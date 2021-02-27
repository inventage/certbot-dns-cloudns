import contextlib
import functools
import logging
import threading

import cloudns_api
import cloudns_api.parameters
import cloudns_api.record
import cloudns_api.validation
from certbot import errors
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

# We're monkey-patching the cloudns library to set auth params programmatically
_auth_params = threading.local()
cloudns_api.api.get_auth_params = \
    cloudns_api.parameters.get_auth_params = \
    cloudns_api.record.get_auth_params = lambda: _auth_params.__dict__


@contextlib.contextmanager
def auth_params(credentials):
    """Context manager to setup and clean up auth params"""
    config_keys = ('auth-id', 'sub-auth-id', 'sub-auth-user', 'auth-password')
    params = dict((key, credentials.conf(key))
                  for key in config_keys
                  if credentials.conf(key) is not None)

    _auth_params.__dict__.update(params)
    try:
        yield params
    finally:
        _auth_params.__dict__.clear()


class ApiErrorResponse(errors.PluginError):
    pass


class ClouDNSClient:
    """
    Encapsulates all communication with the ClouDNS API.
    """

    def __init__(self, credentials):
        self.credentials = credentials

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.

        :param str domain: The domain to be verified.
        :param str record_name: The record name.
        :param str record_content: The record content.
        :param int record_ttl: The record TTL (in seconds).
        :raises certbot.errors.PluginError: if an error occurs.
        """

        zone, host = self._find_zone_and_host(record_name)

        logger.debug(
            'Attempting to add record %s to zone %s (to validate %s).',
            host, zone, domain
        )

        self._api_request(cloudns_api.record.create,
                          domain_name=zone,
                          host=host,
                          record_type='TXT',
                          record=record_content,
                          ttl=record_ttl)

    def del_txt_record(self, domain, record_name, record_content):
        """
        Delete a TXT record using the supplied information.

        Note that both the record's name and content are used to ensure that
        similar records created concurrently (e.g., due to concurrent
        invocations of this plugin) are not deleted.

        Failures are logged, but not raised.

        :param str domain: The domain to be verified.
        :param str record_name: The record name.
        :param str record_content: The record content.
        """

        try:
            zone, host = self._find_zone_and_host(record_name)
        except errors.PluginError as e:
            logger.debug('Encountered error finding zone_id during deletion',
                         exc_info=e)
            return

        record_id = self._find_txt_record_id(zone, host, record_content)
        if record_id:
            try:
                self._api_request(cloudns_api.record.delete,
                                  domain_name=zone,
                                  record_id=record_id)
                logger.debug('Successfully deleted TXT record.')
            except errors.PluginError as e:
                logger.warning(
                    'Encountered CloudFlareAPIError deleting TXT record',
                    exc_info=e
                )
        else:
            logger.debug('TXT record not found; no cleanup needed.')

    @functools.lru_cache(maxsize=None)
    def _find_zone_and_host(self, domain):
        """
        Find the zone and host for a given domain.

        :param str domain: The domain for which to find the zone_id.
        :returns: The zone name and host name, if found.
        :raises certbot.errors.PluginError: if no zone_id is found.
        """
        zone_name_guesses = dns_common.base_domain_name_guesses(domain)

        for zone_name in zone_name_guesses:
            try:
                cloudns_api.validation.is_domain_name(zone_name)
            except cloudns_api.validation.ValidationError:
                continue

            logger.debug(f"Looking up zone {zone_name}.")
            try:
                self._api_request(cloudns_api.zone.get,
                                  domain_name=zone_name)
            except ApiErrorResponse:
                logger.debug(f"Zone {zone_name} not found")
            else:
                logger.debug(f"Found zone {zone_name} for {domain}.")
                return zone_name, domain[:-len(zone_name) - 1]

        raise errors.PluginError(
            f"Unable to find zone for {domain} using zone names: "
            f"{', '.join(zone_name_guesses)}.\n Please confirm that the "
            f"domain name has been entered correctly and is already "
            f"associated with the supplied ClouDNS account."
        )

    def _find_txt_record_id(self, zone, record_name, record_content):
        """
        Find the record_id for a TXT record with the given name and content.

        :param str zone: The zone which contains the record.
        :param str record_name: The record name.
        :param str record_content: The record content.
        :returns: The record_id, if found.
        :rtype: str
        """
        records = self._api_request(cloudns_api.record.list,
                                    domain_name=zone, host=record_name,
                                    record_type='TXT')

        for record_id, record in records.items():
            if record['record'] == record_content:
                return record_id

        logger.debug('Unable to find TXT record.')
        return None

    def _api_request(self, api_method, *args, **kwargs):
        with auth_params(self.credentials):
            try:
                response = api_method(*args, **kwargs)
            except Exception as e:
                raise errors.PluginError(
                    'Error communicating with the ClouDNS API'
                ) from e

        response_content = response.json()
        logger.debug("ClouDNS API response: %s", response_content)

        if self._is_successful(response):
            return response_content.get('payload')
        else:
            raise ApiErrorResponse(
                'Error communicating with the ClouDNS API: {0}'.format(
                    response_content
                )
            )

    @staticmethod
    def _is_successful(response):
        return (
                not response.error
                and response.status_code == 200
        )
