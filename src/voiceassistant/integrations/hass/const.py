"""Host constants."""

DOMAIN = "hass"
CLIENT = "client"
NAME_TO_ENTITY = "name_to_entity"

SERVICES = "services"
STATES = "states"


class ColorMode:
    """Possible light color modes."""

    UNKNOWN = "unknown"  # Ambiguous color mode
    ONOFF = "onoff"  # Must be the only supported mode
    BRIGHTNESS = "brightness"  # Must be the only supported mode
    COLOR_TEMP = "color_temp"
    HS = "hs"
    XY = "xy"
    RGB = "rgb"
    RGBW = "rgbw"
    RGBWW = "rgbww"
    WHITE = "white"  # Must *NOT* be the only supported mode
