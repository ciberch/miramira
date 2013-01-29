

import httplib2
import util
import logging

from model import Credentials, User, CircleRelation
from google.appengine.ext import db

class Alert(object):

   def __init__(self, alert_text, user, *args, **kwargs):
     self.alert_text = alert_text
     self.user = user
     self.circles = []
     self.actions = []


   def withOptionTo(self, action):
      self.actions.append(action)
      return self
       
   def for_(self, circle):
      if isinstance(circle, list):
         self.circles.extend([a for a in circle])
      else:
         self.circles.append(circle)
      return self

   def send(self):
       body = self.construct_body()
       for circle in self.circles:
           body['creator'] = { 'id': self.user.key().name(), 'displayName': self.user.first_name, 'imageUrls': [self.user.photo]}
           self.send_to_circle(body, circle)

   def send_to_circle(self, body, circle):
       circleRels = CircleRelation.gql('WHERE name = :1 AND follower = :2 ', circle, self.user)
       for rel in circleRels:
          logging.info('Sending to a user')
          self.send_body(body, rel.following)
        
   def send_body(self, body, user):
       http = httplib2.Http()
       creds = Credentials.get_by_key_name(user.key().name())
       if creds is None or creds.credentials is None:
          # If the user's auth token expired, just bail and continue on
          logging.error('Sending to a user failed no auth')
          return

       creds.credentials.authorize(http)

       glass_service = util.create_glass_service(http)
       glass_service.timeline().insert(body=body).execute()
       
   def construct_body(self):
       # Sound for Urgency!
       body = {
            'notification': {'level': 'AUDIO_ONLY'},
            'text': self.alert_text,
	    'menuItems': self.actions
          }
       return body
