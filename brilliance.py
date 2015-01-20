import webapp2
import logging
import math
import json
import time

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import ndb

class Calculator(webapp2.RequestHandler):


    def post(self):
        # The server should be agnostic of all relevant client data. We send
        # both points and perfect circle center
        coords = self.request.POST['points']
        center = self.request.POST['center']

        coords = json.loads(coords)
        center = json.loads(center)

        sum = 0
        for coord in coords:
            distance = abs(math.sqrt((center['x'] - coord['x']) ** 2 + (center['y'] -  coord['y']) ** 2) - 150)
            sum += distance**2

        #penalty = (((len(coords)-500)**2)/40) + 1
        penalty = math.e**(0.03*(len(coords)-500))+math.e**(0.03*(-len(coords)+500))-1

        average = (sum/(len(coords))) + 1

        average = int((average * penalty) / 1000000)

        message = {
            'sum': average
        }

        message = json.dumps(message)

        logging.info('coords')
        logging.info(message)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(message)
