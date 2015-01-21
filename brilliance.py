import webapp2
import logging
import math
import json
import time

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import ndb

# This class calculates the brilliance of a circle. It does that by taking into
# account three parameters:
# 1. The distance the user crossed with the mouse. Since we know what a perfect
#    circle looks like, we expect the user to cross a certain amount of pixels
#    with the mouse. We can then compare that distance crossed, with the perimeter
#    of the perfect circle.
# 2. The distance of all the points, to the closest point of the circle. Again,
#    we know what the perfect circle looks like, and we expect the drawn points
#    to be as close as possible to that one.
# 3. Whether the user passed through all the quadrants or not. This is just an
#    extra way to protect against an exploit of the game logic, by staying at the
#    same area of the canvas.
#
# These parameters are then evaluated against a weight.
class Calculator(webapp2.RequestHandler):

    DISTANCE_CROSSED_WEIGHT = 0.5
    DISTANCE_TO_CIRCLE_WEIGHT = 100
    QUADRAND_PENALTY_WEIGHT = 30

    def calculate(self, center, radius, points, canvasSize):

        pointToCircleDistError = 0
        check = False
        drawDistance = 0
        prevPoint = {'x': 0, 'y': 0}

        # The 4 quadrants of a circle, up-right, down-right, etc
        quadrant = {'ur': False, 'dr': False, 'dl': False, 'ul': False}
        # Quadrant oenalty starts from 5 and decreases as we find points in
        # the quadrants
        quadrantPenalty = 5;

        # Go through all the points and get data needed for applying penalties
        for point in points:

            # Get distance between each point, and add add it
            if check == False:
                check = True
            else:
                drawDistance += math.sqrt((point['x'] - prevPoint['x'])**2 + \
                                          (point['y'] - prevPoint['y'])**2)

            prevPoint['x'] = point['x']
            prevPoint['y'] = point['y']

            pointToCircleDist = abs(math.sqrt((center['x'] - point['x']) ** 2 + \
                                              (center['y'] - point['y']) ** 2) - radius)

            pointToCircleDistError += pointToCircleDist ** 2

            # "Move" the circle to the center of the axes, and check for points
            # in the quadrants
            x = point['x'] - int(canvasSize['x']/2)
            y = int(canvasSize['y']/2) - point['y'] # point 0.0 starts from top left
            if x >= 0 and y >= 0 and not quadrant['ur']:
                quadrant['ur'] = True;
                quadrantPenalty -= 1;
            elif x >= 0 and y < 0 and not quadrant['dr']:
                quadrant['dr'] = True;
                quadrantPenalty -= 1;
            elif x < 0 and y <= 0 and not quadrant['dl']:
                quadrant['dl'] = True;
                quadrantPenalty -= 1;
            elif x < 0 and y > 0 and not quadrant['ul']:
                quadrant['ul'] = True;
                quadrantPenalty -= 1;

        # Calculate penalties
        perimeter = 2 * math.pi * radius;
        distanceCrossedPenalty = abs(drawDistance - perimeter) * \
                                 self.DISTANCE_CROSSED_WEIGHT

        quadrantPenalty = (quadrantPenalty ** 2 ) * self.QUADRAND_PENALTY_WEIGHT

        distanceToCirclePenalty = pointToCircleDistError / \
                                  (len(points) * self.DISTANCE_TO_CIRCLE_WEIGHT)

        score = distanceToCirclePenalty + quadrantPenalty + distanceCrossedPenalty

        # Score will be inverted later on, so we need to make sure it bigger than one
        score = score/100 + 1

        return score


    def post(self):
        # The server should be agnostic of all relevant client data. We receive
        # both points and perfect circle info
        points = self.request.POST['points']
        center = self.request.POST['center']
        radius = self.request.POST['radius']
        canvasSize = self.request.POST['canvasSize']

        points = json.loads(points)
        center = json.loads(center)
        radius = json.loads(radius)
        canvasSize = json.loads(canvasSize)

        # calculate rates circles with lowest score being the best, so we need to
        # invert that
        score = int(( 1 / self.calculate(center, radius, points, canvasSize)) * 1000)

        # By trial and error, we checked the smallest error we can have is around
        # 67. We can calibrate the results further, subtracting it.
        score -= 66

        message = {
            'score': score
        }

        message = json.dumps(message)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(message)
