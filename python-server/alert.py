

import httplib2
import util
from model import User
from google.appengine.extras import db

class Alert(object):

   def __init__(self, alert_text, *args, **kwargs):
     self.alert_text = alert_text
     self.circles = []


   def add_to(self, circle):
      self.circles.append(circle)

   def send(self):
       body = self.construct_body()
       for circle in self.circles:
           body['creator'] = { 'id': circle, 'display_name': circle.upper()}
           self.send_to_circle(body, circle):

   def send_circle(self, body, cirlce):
       query = db.Query(User)
       users = query.all().filter('circles=', circle).run()
       for user in users:
          self.send_body(body, user)
        
   def send_body(self, body, user):
       http = httplib2.Http()
       creds = Credential.get_by_key_name(user.key_name())
       if creds is None:
          # If the user's auth token expired, just bail and continue on
          return

       creds.auth(http)
       glass_service = util.get_glass_service(creds)
       glass_service.timeline().insert(body=body).execute()
       
   def _construct_body():
       # Sound for Urgency!
       body = {
        'notification': {'level': 'AUDIO_ONLY'},
        'text': self.alert_text,
	'menuItems': [
              # System action to reply to the alert (ACK!),
              # The server will receive the audio response from the user and a transciption of it.
              {
                action: 'REPLY',
              }
         ] 
        }
        return body 
