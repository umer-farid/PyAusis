"""
Plugins not fully converted but simply "wrapped" as plugins.
"""
from packages import (directions_to, forecast, mapps, near_me,
                      timeIn, weather_pinpoint, weatherIn)

from plugin import plugin, require


@require(network=True)
@plugin("check time")
def check_time(self, s):
    """
    checks the current time in any part of the globe.
    -- Examples:
        check time in Manchester (UK)
    """
    timeIn.main(self._ausis, s)


@require(network=True)
@plugin("check forecast")
def check_forecast(self, s):
    """
    checks the weather forecast for the next 7 days.
    -- Examples:
        check forecast
        check forecast in Madrid
    """
    forecast.main(self, s)


@require(network=True)
@plugin("check weather")
def check_weather(self, s):
    """
    weather in *: checks the current weather in any part of the globe.
    -- Examples:
        check weather in Canada
    """
    weatherIn.main(self._ausis, s)


@require(network=True)
@plugin("directions")
def directions(self, data):
    """
    Get directions about a destination you are interested to.
    -- Example:
        directions to the Eiffel Tower
    """
    self = self._ausis

    try:
        directions_to.main(data)
    except ValueError:
        print("Please enter destination")


@require(network=True)
@plugin("near")
def do_near(self, data):
    """
    ausis can find what is near you!
    -- Examples:
        restaurants near me
        museums near the eiffel tower
    """
    near_me.main(data)


@require(network=True)
@plugin("pinpoint")
def do_pinpoint(self, s):
    """ausis will pinpoint your location."""
    mapps.locate_me()


@require(network=True)
@plugin("umbrella")
def do_umbrella(self, s):
    """If you're leaving your place, ausis will inform you if you might need an umbrella or not."""
    self = self._ausis

    s = 'umbrella'
    weather_pinpoint.main(self.memory, self, s)


@plugin("update location")
def do_update(ausis, s):
    """
    location: Updates location.
    system: Updates system.
    """
    location = ausis.get_data('city')
    loc_str = str(location)
    ausis.say("Your current location is set to " + loc_str)
    ausis.say("What is your new location?")
    i = ausis.input()
    ausis.update_data('city', i)


@require(network=True)
@plugin("weather")
def do_weather(self, s):
    """Get information about today's weather in your current location."""
    self = self._ausis

    word = s.strip()
    if(len(word) > 1):
        weatherIn.main(self, s)
    else:
        weather_pinpoint.main(self.memory, self, s)
