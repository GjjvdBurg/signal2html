# -*- coding: utf-8 -*-

"""Colors extracted from Signal source

License: See LICENSE file.

"""

import logging
import random

logger = logging.getLogger(__name__)

CRIMSON = "#CC163D"
CRIMSON_TINT = "#EDA6AE"
CRIMSON_SHADE = "#8A0F29"
VERMILLION = "#C73800"
VERMILLION_TINT = "#EBA78E"
VERMILLION_SHADE = "#872600"
BURLAP = "#746C53"
BURLAP_TINT = "#C4B997"
BURLAP_SHADE = "#58513C"
FOREST = "#3B7845"
FOREST_TINT = "#8FCC9A"
FOREST_SHADE = "#2B5934"
WINTERGREEN = "#1C8260"
WINTERGREEN_TINT = "#9BCFBD"
WINTERGREEN_SHADE = "#36544A"
TEAL = "#067589"
TEAL_TINT = "#A5CAD5"
TEAL_SHADE = "#055968"
BLUE = "#336BA3"
BLUE_TINT = "#ADC8E1"
BLUE_SHADE = "#285480"
INDIGO = "#5951C8"
INDIGO_TINT = "#C2C1E7"
INDIGO_SHADE = "#4840A0"
VIOLET = "#862CAF"
VIOLET_TINT = "#CDADDC"
VIOLET_SHADE = "#6B248A"
PLUMB = "#A23474"
PLUMB_TINT = "#DCB2CA"
PLUMB_SHADE = "#881B5B"
TAUPE = "#895D66"
TAUPE_TINT = "#CFB5BB"
TAUPE_SHADE = "#6A4E54"
STEEL = "#6B6B78"
STEEL_TINT = "#BEBEC6"
STEEL_SHADE = "#5A5A63"
ULTRAMARINE = "#2C6BED"
ULTRAMARINE_TINT = "#B0C8F9"
ULTRAMARINE_SHADE = "#1851B4"
GROUP = "#2C6BED"
GROUP_TINT = "#B0C8F9"
GROUP_SHADE = "#1851B4"

COLORMAP = {
    "red": CRIMSON,
    "deep_orange": CRIMSON,
    "orange": VERMILLION,
    "amber": VERMILLION,
    "brown": BURLAP,
    "yellow": BURLAP,
    "pink": PLUMB,
    "purple": VIOLET,
    "deep_purple": VIOLET,
    "indigo": INDIGO,
    "blue": BLUE,
    "light_blue": BLUE,
    "cyan": TEAL,
    "teal": TEAL,
    "green": FOREST,
    "light_green": WINTERGREEN,
    "lime": WINTERGREEN,
    "blue_grey": TAUPE,
    "grey": STEEL,
    "ultramarine": ULTRAMARINE,
    "group_color": GROUP,
}

# Extracted from:
# https://github.com/signalapp/Signal-Android/blob/master/app/src/main/java/org/thoughtcrime/securesms/conversation/colors/AvatarColor.java
# Note that Signal uses ColorInts, which are AARRGGBB. We strip off the alpha.
AVATAR_COLORS = {
    "C000": "#D00B0B",
    "C010": "#C72A0A",
    "C020": "#B34209",
    "C030": "#9C5711",
    "C040": "#866118",
    "C050": "#76681E",
    "C060": "#6C6C13",
    "C070": "#5E6E0C",
    "C080": "#507406",
    "C090": "#3D7406",
    "C100": "#2D7906",
    "C110": "#1A7906",
    "C120": "#067906",
    "C130": "#067919",
    "C140": "#06792D",
    "C150": "#067940",
    "C160": "#067953",
    "C170": "#067462",
    "C180": "#067474",
    "C190": "#077288",
    "C200": "#086DA0",
    "C210": "#0A69C7",
    "C220": "#0D59F2",
    "C230": "#3454F4",
    "C240": "#5151F6",
    "C250": "#6447F5",
    "C260": "#7A3DF5",
    "C270": "#8F2AF4",
    "C280": "#A20CED",
    "C290": "#AF0BD0",
    "C300": "#B80AB8",
    "C310": "#C20AA3",
    "C320": "#C70A88",
    "C330": "#CB0B6B",
    "C340": "#D00B4D",
    "C350": "#D00B2C",
    "crimson": "#CF163E",
    "vermilion": "#C73F0A",
    "burlap ": "#6F6A58",
    "forest ": "#3B7845",
    "wintergreen": "#1D8663",
    "teal": "#077D92",
    "blue": "#336BA3",
    "indigo ": "#6058CA",
    "violet ": "#9932CB",
    "plum": "#AA377A",
    "taupe": "#8F616A",
    "steel": "#71717F",
    "unknown": "#71717F",
}


def list_colors():
    return sorted(set(list(COLORMAP.keys()) + list(AVATAR_COLORS.keys())))


def get_color(name):
    color = COLORMAP.get(name, None) or AVATAR_COLORS.get(name, None)
    if not color is None:
        return color
    logger.warn(f"Unknown color: {name}, using fallback color instead.")
    return AVATAR_COLORS["unknown"]


def get_random_color():
    return random.choice(list(COLORMAP.keys()))
