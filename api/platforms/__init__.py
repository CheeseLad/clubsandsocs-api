import enum


class Platform(enum.Enum):
    """The platform powering a clubs & societies site."""

    ASSURE = "assure"
    RUBRIC = "rubric"


RUBRIC_SITES: frozenset[str] = frozenset(
    {
        "dcuclubsandsocs.ie",
    }
)


def get_platform(site: str) -> Platform:
    """Return the platform used by `site`."""
    if site in RUBRIC_SITES:
        return Platform.RUBRIC
    return Platform.ASSURE
