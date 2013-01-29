

import httplib2
import util
from model import Credentials, User
from google.appengine.ext import db

class Alert(object):

   def __init__(self, alert_text, *args, **kwargs):
     self.alert_text = alert_text
     self.circles = []
     self.actions = []


   def withOptionTo(self, action):
      self.actions.append(action)
      return self
       
   def for_(self, circle):
      if isinstance(circle, list):
         self.circles.extend([a.upper() for a in circle])
      else:
         self.circles.append(circle.upper())
      return self

   def send(self):
       body = self.construct_body()
       for circle in self.circles:
           body['creator'] = { 'id': circle, 'display_name': circle}
           self.send_to_circle(body, circle)

   def send_to_circle(self, body, circle):
       users = User.gql('WHERE circles = :1', circle)
       for user in users:
          self.send_body(body, user)
        
   def send_body(self, body, user):
       http = httplib2.Http()
       creds = Credentials.get_by_key_name(user.key().name())
       if creds is None or creds.credentials is None:
          # If the user's auth token expired, just bail and continue on
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
