"""REST client handling, including BitlyStream base class."""

from __future__ import annotations

from singer_sdk import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator


class BitlyStream(RESTStream):
    """Bitly stream class."""

    url_base = "https://api-ssl.bitly.com"
    records_jsonpath = "$[*]"
    next_page_token_jsonpath = "$.next_page"
    _page_size = 100

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        token: str = self.config["token"]
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=token,
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        headers["User-Agent"] = f"{self.tap_name}/{self._tap.plugin_version}"
        return headers
