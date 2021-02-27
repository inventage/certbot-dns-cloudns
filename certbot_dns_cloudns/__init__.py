__version__ = '0.1.0'

"""
The `~certbot_dns_clounds.dns_cloudns` plugin automates the process of
completing a ``dns-01`` challenge (`~acme.challenges.DNS01`) by creating, and
subsequently removing, TXT records using the ClouDNS API.

Named Arguments
---------------
===================================== =====================================
``--dns-cloudns-credentials``         ClouDNS credentials_ INI file.
                                      (Required)
``--dns-cloudns-propagation-seconds`` The number of seconds to wait for DNS
                                      to propagate before asking the ACME
                                      server to verify the DNS record.
                                      (Default: 60)
===================================== =====================================
Credentials
-----------
Use of this plugin requires a configuration file containing the ClouDNS API
credentials.
.. code-block:: ini
   :name: credentials.ini
   :caption: Example credentials file:
   # Target user ID (see https://www.cloudns.net/api-settings/)
   dns_cloudns_auth_id=1234
   # Alternatively, one of the following two options can be set:
   # dns_cloudns_sub_auth_id=1234
   # dns_cloudns_sub_auth_user=foobar
   
   # API password 
   dns_cloudns_auth_password=password1

The path to this file can be provided interactively or using the
``--dns-cloudns-credentials`` command-line argument. Certbot records the
path to this file for use during renewal, but does not store the file's 
contents.
.. caution::
   You should protect your credentials, as they can be used to potentially
   add, update, or delete any record in the target DNS server. Users who can
   read this file can use these credentials to issue arbitrary API calls on
   your behalf. Users who can cause Certbot to run using these credentials can
   complete a ``dns-01`` challenge to acquire new certificates or revoke
   existing certificates for associated domains, even if those domains aren't
   being managed by this server.
Certbot will emit a warning if it detects that the credentials file can be
accessed by other users on your system. The warning reads "Unsafe permissions
on credentials configuration file", followed by the path to the credentials
file. This warning will be emitted each time Certbot uses the credentials file,
including for renewal, and cannot be silenced except by addressing the issue
(e.g., by using a command like ``chmod 600`` to restrict access to the file).
'''''''''''''''''''''''''
Examples
--------
.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``
   certbot certonly \\
     --dns-cloudns \\
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \\
     -d example.com
.. code-block:: bash
   :caption: To acquire a single certificate for both ``example.com`` and
             ``www.example.com``
   certbot certonly \\
     --dns-cloudns \\
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \\
     -d example.com \\
     -d www.example.com
.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``, waiting 30 seconds
             for DNS propagation
   certbot certonly \\
     --dns-cloudns \\
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \\
     --dns-cloudns-propagation-seconds 30 \\
     -d example.com
"""
