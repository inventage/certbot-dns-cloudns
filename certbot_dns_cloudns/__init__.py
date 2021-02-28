"""
The `~certbot_dns_clounds.dns_cloudns` plugin automates the process of
completing a ``dns-01`` challenge (`~acme.challenges.DNS01`) by creating, and
subsequently removing, TXT records using the ClouDNS API.

Named Arguments
---------------
===================================== =====================================
``--dns-cloudns-credentials``         ClouDNS credentials_ INI file.
                                      `(Required)`
``--dns-cloudns-propagation-seconds`` The number of seconds to wait for DNS
                                      to propagate before asking the ACME
                                      server to verify the DNS record.
                                      `(Default: 60)`
``--dns-cloudns-nameserver``          Nameserver used to resolve CNAME
                                      aliases. (See the
                                      `Challenge Delegation`_ section
                                      below.)
                                      `(Default: System default)`
===================================== =====================================

Credentials
-----------
Use of this plugin requires a configuration file containing the ClouDNS API
credentials.

.. code-block:: ini

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

Challenge Delegation
--------------------
The dns-cloudns plugin supports delegation of ``dns-01`` challenges to
other DNS zones through the use of CNAME records.

As stated in the `Let's Encrypt documentation
<https://letsencrypt.org/docs/challenge-types/#dns-01-challenge>`_:

    Since Let’s Encrypt follows the DNS standards when looking up TXT records
    for DNS-01 validation, you can use CNAME records or NS records to delegate
    answering the challenge to other DNS zones. This can be used to delegate
    the _acme-challenge subdomain to a validation-specific server or zone. It
    can also be used if your DNS provider is slow to update, and you want to
    delegate to a quicker-updating server.

This allows the credentials provided to certbot to be limited to either a
sub-zone of the verified domain, or even a completely separate throw-away
domain. This idea is further discussed in `this article
<https://www.eff.org/deeplinks/2018/02/
technical-deep-dive-securing-automation-acme-dns-challenge-validation>`_
by the `Electronic Frontier Foundation <https://www.eff.org>`_.

To resolve CNAME aliases properly, Certbot needs to be able to access a public
DNS server. In some setups, especially corporate networks, the challenged
domain might be resolved by a local server instead, hiding configured CNAME and
TXT records from Certbot. In these cases setting the
``--dns-cloudns-nameserver`` option to any public nameserver (e.g. ``1.1.1.1``)
should resolve the issue.

Examples
--------

.. code-block:: bash

   certbot certonly \
     --dns-cloudns \
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \
     -d example.com

.. code-block:: bash

   certbot certonly \
     --dns-cloudns \
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \
     -d example.com \
     -d www.example.com

.. code-block:: bash

   certbot certonly \
     --dns-cloudns \
     --dns-cloudns-credentials ~/.secrets/certbot/cloudns.ini \
     --dns-cloudns-propagation-seconds 30 \
     -d example.com
"""
