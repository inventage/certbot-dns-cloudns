import functools
import logging

import dns.resolver
import dns.name
from certbot import errors

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=None)
def resolve_alias(domain_name, nameserver):
    """
    Performs recursive CNAME lookups for a given domain name.
    """
    resolver = _get_resolver(nameserver)
    name = dns.name.from_text(domain_name)

    while True:
        try:
            records = resolver.resolve(name, 'CNAME')
            if len(records) > 1:
                raise errors.PluginError(
                    f"Name {name} has multiple CNAME records set: "
                    f"{', '.join(record.target for record in records)}"
                )
            elif len(records) == 1:
                resolved_name = records[0].target
                logger.debug(f"{name} points to {resolved_name}")
                name = resolved_name
            else:
                break
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            logger.debug(f"No CNAME record found for {name}")
            break

    return name.to_text(omit_final_dot=True)


@functools.lru_cache(maxsize=None)
def _get_resolver(nameserver):
    if nameserver is None:
        resolver = dns.resolver.Resolver()
    else:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers.append(nameserver)

    logger.debug(
        f"Using nameserver{'s' if len(resolver.nameservers) > 1 else ''} "
        f"{', '.join(resolver.nameservers)}"
    )
    return resolver
