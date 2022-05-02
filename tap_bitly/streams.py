"""Stream type classes for tap-bitly."""

from typing import Any, Dict, Iterable, Optional
from urllib.parse import parse_qs, urlparse

import requests
from singer_sdk import typing as th

from tap_bitly.client import BitlyStream


class Groups(BitlyStream):
    """Users stream."""

    name = "groups"
    path = "/v4/groups"
    primary_keys = ["guid"]
    records_jsonpath = "$.groups[*]"
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "guid",
            th.StringType,
            description="The group's unique identifier.",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The group's name.",
        ),
        th.Property(
            "references",
            th.ObjectType(
                th.Property("organization", th.StringType),
            ),
            description="Mapping of group references.",
        ),
        th.Property(
            "created",
            th.DateTimeType,
            description="The date and time the group was created.",
        ),
        th.Property(
            "modified",
            th.DateTimeType,
            description="The date and time the group was last modified.",
        ),
        th.Property(
            "bsds",
            th.ArrayType(th.StringType),
            description="The group's branded short domains.",
        ),
        th.Property(
            "organization_guid",
            th.StringType,
            description="The group's organization's unique identifier.",
        ),
        th.Property(
            "is_active",
            th.BooleanType,
            description="Whether the group is active.",
        ),
        th.Property(
            "role",
            th.StringType,
            description="The group's role.",
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict] = None) -> dict:
        """Get child context for a record.

        Args:
            record: The record to get child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"group_guid": record["guid"]}


class Bitlinks(BitlyStream):
    """Bitlinks stream."""

    name = "bitlinks"
    path = "/v4/groups/{group_guid}/bitlinks"
    primary_keys = ["id"]
    records_jsonpath = "$.links[*]"
    replication_key = None
    parent_stream_type = Groups

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The bitlink's unique identifier.",
        ),
        th.Property(
            "created_at",
            th.DateTimeType,
            description="The date and time the bitlink was created.",
        ),
        th.Property("link", th.StringType, description="The bitlink's URL."),
        th.Property(
            "custom_bitlinks",
            th.ArrayType(th.StringType),
            description="The bitlink's custom bitlinks.",
        ),
        th.Property("long_url", th.StringType, description="The bitlink's URL."),
        th.Property("title", th.StringType, description="The bitlink's title."),
        th.Property(
            "archived",
            th.BooleanType,
            description="Whether the bitlink is archived.",
        ),
        th.Property("created_by", th.StringType, description="The bitlink's creator."),
        th.Property("client_id", th.StringType, description="The bitlink's client ID."),
        th.Property(
            "tags",
            th.ArrayType(th.StringType),
            description="The bitlink's tags.",
        ),
        th.Property(
            "deeplinks",
            th.ArrayType(th.StringType),
            description="The bitlink's deeplinks.",
        ),
        th.Property(
            "references",
            th.ObjectType(th.Property("group", th.StringType)),
            description="Mapping of bitlink references.",
        ),
        th.Property("group_guid", th.StringType, description="The bitlink's group."),
    ).to_dict()

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Optional[int]:
        """Get the next page token for a response.

        Args:
            response: The response to get the next page token for.
            previous_token: The previous page token.

        Returns:
            The next page token.
        """
        next_url = response.json().get("pagination", {}).get("next")

        if next_url:
            qs_data = parse_qs(urlparse(next_url).query)
            return int(qs_data["page"][0])

        return None

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Get URL parameters.

        Args:
            context: The stream sync context.
            next_page_token: The next page token.

        Returns:
            The URL parameters.
        """
        return {
            "archived": "both",
            "size": self._page_size,
            "page": next_page_token or 1,
        }

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Get child context for a record.

        Args:
            record: The record to get child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"bitlink": record["id"]}


class BrandedShortDomains(BitlyStream):
    """Branded Short Domains stream."""

    name = "bsds"
    path = "/v4/bsds"
    primary_keys = ["domain"]

    schema = th.PropertiesList(
        th.Property(
            "domain",
            th.StringType,
            description="The branded short domain.",
            required=True,
        ),
    ).to_dict()

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse response for a request.

        Args:
            response: The response to parse.

        Yields:
            The parsed records.
        """
        for bsd in response.json()["bsds"]:
            yield {"domain": bsd}


class Campaigns(BitlyStream):
    """Campaigns stream."""

    name = "campaigns"
    path = "/v4/campaigns"
    primary_keys = ["guid"]
    records_jsonpath = "$.campaigns[*]"

    schema = th.PropertiesList(
        th.Property(
            "guid",
            th.StringType,
            description="The campaign's unique identifier.",
            required=True,
        ),
        th.Property(
            "group_guid",
            th.StringType,
            description="The campaign's group.",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The campaign's name.",
        ),
        th.Property(
            "description",
            th.StringType,
            description="The campaign's description.",
        ),
        th.Property(
            "created",
            th.DateTimeType,
            description="The date and time the campaign was created.",
        ),
        th.Property(
            "modified",
            th.DateTimeType,
            description="The date and time the campaign was last modified.",
        ),
        th.Property(
            "created_by",
            th.StringType,
            description="The campaign's creator.",
        ),
        th.Property(
            "references",
            th.ObjectType(
                # th.Property("group", th.StringType),
            ),
            description="Mapping of campaign references.",
        ),
    ).to_dict()


class Organizations(BitlyStream):
    """Organizations stream."""

    name = "organizations"
    path = "/v4/organizations"
    primary_keys = ["guid"]
    records_jsonpath = "$.organizations[*]"

    schema = th.PropertiesList(
        th.Property(
            "guid",
            th.StringType,
            description="The organization's unique identifier.",
        ),
        th.Property(
            "references",
            th.ObjectType(
                th.Property(
                    "groups",
                    th.StringType,
                    description="The organization's groups.",
                )
            ),
            description="Mapping of organization references.",
        ),
        th.Property("name", th.StringType, description="The organization's name."),
        th.Property(
            "is_active",
            th.BooleanType,
            description="Whether the organization is active.",
        ),
        th.Property("tier", th.StringType, description="The organization's tier."),
        th.Property(
            "tier_family",
            th.StringType,
            description="The organization's tier family.",
        ),
        th.Property(
            "tier_display_name",
            th.StringType,
            description="The organization's tier display name.",
        ),
        th.Property(
            "role",
            th.StringType,
            description="The organization's role.",
        ),
        th.Property(
            "created",
            th.DateTimeType,
            description="The date and time the organization was created.",
        ),
        th.Property(
            "modified",
            th.DateTimeType,
            description="The date and time the organization was last modified.",
        ),
        th.Property(
            "bsds",
            th.ArrayType(th.StringType),
            description="The organization's branded short domains.",
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Get child context for a record.

        Args:
            record: The record to get child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"organization_guid": record["guid"]}


class Webhooks(BitlyStream):
    """Webhooks stream."""

    name = "webhooks"
    path = "/v4/organizations/{organization_guid}/webhooks"
    primary_keys = ["guid"]
    records_jsonpath = "$.webhooks[*]"
    parent_stream_type = Organizations

    schema = th.PropertiesList(
        th.Property(
            "guid",
            th.StringType,
            description="The webhook's unique identifier.",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The webhook's name.",
        ),
        th.Property(
            "references",
            th.ObjectType(),
            description="Mapping of webhook references.",
        ),
        th.Property(
            "created",
            th.DateTimeType,
            description="The date and time the webhook was created.",
        ),
        th.Property(
            "modified",
            th.DateTimeType,
            description="The date and time the webhook was last modified.",
        ),
        th.Property(
            "modified_by",
            th.StringType,
            description="The webhook's modifier.",
        ),
        th.Property(
            "deactivated",
            th.DateTimeType,
            description="The date and time the webhook was deactivated.",
        ),
        th.Property(
            "is_active",
            th.BooleanType,
            description="Whether the webhook is active.",
        ),
        th.Property(
            "organization_guid",
            th.StringType,
            description="The webhook's organization.",
        ),
        th.Property(
            "group_guid",
            th.StringType,
            description="The webhook's group.",
        ),
        th.Property(
            "event",
            th.StringType,
            description="The webhook's event.",
        ),
        th.Property(
            "url",
            th.StringType,
            description="The webhook's URL.",
        ),
        th.Property(
            "status",
            th.StringType,
            description="The webhook's status.",
        ),
        th.Property(
            "oauth_url",
            th.StringType,
            description="The webhook's OAuth URL.",
        ),
        th.Property(
            "client_id",
            th.StringType,
            description="The webhook's client ID.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            description="The webhook's client secret.",
        ),
        th.Property(
            "fetch_tags",
            th.BooleanType,
            description="Whether to fetch tags.",
        ),
    ).to_dict()


class DailyBitlinkClicks(BitlyStream):
    """Daily bitlink clicks."""

    name = "daily_bitlink_clicks"
    path = "/v4/bitlinks/{bitlink}/clicks"
    primary_keys = ["date", "bitlink"]
    records_jsonpath = "$.link_clicks[*]"
    parent_stream_type = Bitlinks

    schema = th.PropertiesList(
        th.Property("clicks", th.IntegerType, description="The number of clicks."),
        th.Property("date", th.DateTimeType, description="The date."),
        th.Property("bitlink", th.StringType, description="The bitlink."),
    ).to_dict()


class MonthlyBitlinkClicks(DailyBitlinkClicks):
    """Monthly bitlink clicks."""

    name = "montly_bitlink_clicks"

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Get URL parameters.

        Args:
            context: The stream sync context.
            next_page_token: The next page token.

        Returns:
            The URL parameters.
        """
        return {"unit": "month"}
