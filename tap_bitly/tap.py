"""Bitly tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_bitly import streams


class TapBitly(Tap):
    """Singer tap for Bitly."""

    name = "tap-bitly"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Bitly",
        ),
        th.Property(
            "include_paid_streams",
            th.BooleanType,
            default=False,
            description="Whether to sync paid streams",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Bitly streams.
        """
        bitly_streams = [
            streams.Groups(self),
            streams.Bitlinks(self),
            streams.BrandedShortDomains(self),
            streams.Campaigns(self),
            streams.Organizations(self),
            streams.DailyBitlinkClicks(self),
            streams.MonthlyBitlinkClicks(self),
        ]

        if self.config.get("include_paid_streams"):
            bitly_streams.append(streams.Webhooks(self))

        return bitly_streams
