# -*- coding: utf-8 -*-

import os
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Job(object):
    def __init__(self, data, https):
        self._data = data
        self._https = https

    @staticmethod
    def health_to_icon(health, color):
        """Return the correct icon corresponding with the health/color
        Keyword arguments
        health  -- The health of the job
        color   -- The color of the job
        """
        if color == "disabled":
            color = "grey"

        if health >= 0 and health <= 20:
            icon = "images/health-00to19-" + color + ".png"
        elif health > 20 and health <= 40:
            icon = "images/health-20to39-" + color + ".png"
        elif health > 40 and health <= 60:
            icon = "images/health-40to59-" + color + ".png"
        elif health > 60 and health <= 80:
            icon = "images/health-60to79-" + color + ".png"
        elif health > 80:
            icon = "images/health-80plus-" + color + ".png"
        else:
            icon = "images/" + color + ".png"

        return icon

    @property
    def name(self):
        return urllib.unquote(self._data.get('name', ''))

    @property
    def url(self):
        url = self._data.get('url')
        if self._https:
            return url.replace("http://", "https://")
        return url

    @property
    def status(self):
        return self._data.get('color')

    @property
    def image(self):
        if 'healthReport' in self._data and len(self._data.get('healthReport')) > 0:
            return self.health_to_icon(self._data["healthReport"][0]["score"], self._data["color"])
        return "{}/images/{}.png".format(os.getcwdu(), self.status)

    @property
    def description(self):
        return self._data['healthReport'][0]['description']

