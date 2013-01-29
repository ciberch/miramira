# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /main endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import jinja2
import logging
import os
from urlparse import urlparse
import webapp2
import alert

from google.appengine.api import urlfetch

from apiclient.http import MediaIoBaseUpload

from model import User

import util


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainHandler(webapp2.RequestHandler):
  """Request Handler for the main endpoint."""

  def _render_template(self, message=None):
    """Render the main page template."""
    pr = urlparse(self.request.url)
    template_values = {'appBaseUrl': pr.netloc, 'user': self.userModel}
    if message:
      template_values['message'] = message
    # self.glass_service is initialized in util.auth_required.
    shareTargets = self.glass_service.shareTargets().list().execute()
    if shareTargets.get('items'):
      template_values['shareTargets'] = shareTargets['items']

    timeline_items = self.glass_service.timeline().list(maxResults=5).execute()
    if timeline_items.get('items'):
      items = timeline_items['items']
      template_values['timelineItems'] = items

    subscriptions = self.glass_service.subscriptions().list().execute()
    if subscriptions.get('items'):
      template_values['subscriptions'] = subscriptions['items']

    allUsers = User.all()
    if( allUsers ):
        template_values['allUsers'] = allUsers
      
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))

  def _get_full_url(self, path, https=False):
    """Return the full url from the provided path."""
    pr = urlparse(self.request.url)
    return '%s://%s%s' % (pr.scheme if not https else 'https', pr.netloc, path)

  @util.auth_required
  def get(self):
    """Render the main page."""
    try:
      self._insert_subscription()
    except:
      x = 1
    self._render_template()

  @util.auth_required
  def post(self):
    """Execute the request and render the template."""
    operation = self.request.get('operation')
    # Dict of operations to easily map keys to methods.
    operations = {
        'insertSubscription': self._insert_subscription,
        'deleteSubscription': self._delete_subscription,
        'insertItem': self._insert_item,
        'insertItemWithAction': self._insert_item_with_action,
        'insertShareTarget': self._insert_share_target,
        'deleteShareTarget': self._delete_share_target,
        'team_send': self._send_circle_message,
        'teamAddUser': self._add_user_to_team
    }
    if operation in operations:
      message = operations[operation]()
    else:
      message = "I don't know how to " + operation
    self._render_template(message)

  def _insert_subscription(self):
    """Subscribe the app."""
    # self.userid is initialized in util.auth_required.
    body = {
        'verifyCode': 'API',
        'collection': 'timeline',
        'userToken': self.userid,
        'callbackUrl': self._get_full_url('/notify')
    }
    # self.glass_service is initialized in util.auth_required.
    self.glass_service.subscriptions().insert(body=body).execute()
    body['collection'] = 'locations'
    self.glass_service.subscriptions().insert(body=body).execute()
    return 'Application is now subscribed to updates.'

  def _delete_subscription(self):
    """Unsubscribe from notifications."""
    collection = self.request.get('subscriptionId')
    self.glass_service.subscriptions().delete(id=collection).execute()
    return 'Application has been unsubscribed.'

  def _insert_item(self):
    """Insert a timeline item."""
    logging.info('Inserting Timeline Item')
    body = {
        'notification': {'level': 'AUDIO_ONLY'}
    }
    if self.request.get('html') == 'on':
      body['html'] = [self.request.get('message')]
    else:
      body['text'] = self.request.get('message')

    media_link = self.request.get('imageUrl')
    if media_link:
      if media_link.startswith('/'):
        media_link = self._get_full_url(media_link)
      resp = urlfetch.fetch(media_link, deadline=20)
      media = MediaIoBaseUpload(
          io.BytesIO(resp.content), mimetype='image/jpeg', resumable=True)
    else:
      media = None

    # self.glass_service is initialized in util.auth_required.
    self.glass_service.timeline().insert(body=body, media_body=media).execute()
    return  'A timeline item has been inserted.'

  def _insert_item_with_action(self):
    """Insert a timeline item user can reply to."""
    logging.info('Inserting Timeline Item')
    body = {
        'creator': {
            'displayName': 'Python Starter Project',
            'id': 'PYTHON_STARTER_PROJECT'
        },
        'text': 'Tell me what you had for lunch :)',
        'notification': {'level': 'AUDIO_ONLY'},
        'menuItems': [{'action': 'REPLY'}]
    }
    # self.glass_service is initialized in util.auth_required.
    self.glass_service.timeline().insert(body=body).execute()
    return 'A timeline item with action has been inserted.'

  def _send_circle_message(self):
    actions = [{
	'action': 'REPLY',
        }]
    self._send_alert(self.request.get('message'), self.request.get('team', '').split(','), actions=actions)

  def _send_alert(self, message_text, circles, actions=[]):
    logging.info('Inserting alert to %s' % circles)
    a = alert.Alert(message_text, self.user).for_(circles)
    for action in actions:
        a.withOptionTo(action)
    a.send()
    
  def _insert_share_target(self):
    """Insert a new ShareTarget."""
    logging.info('Inserting share target Item')
    name = self.request.get('name')
    image_url = self.request.get('imageUrl')
    if not name or not image_url:
      return 'Must specify imageUrl and name to insert share target'
    else:
      if image_url.startswith('/'):
        image_url = self._get_full_url(image_url)
      body = {
          'id': name,
          'displayName': name,
          'imageUrls': [image_url]
      }
      # self.glass_service is initialized in util.auth_required.
      self.glass_service.shareTargets().insert(body=body).execute()
      return 'Inserted share target: ' + name

  def _delete_share_target(self):
    """Delete a ShareTarget."""
    # self.glass_service is initialized in util.auth_required.
    self.glass_service.shareTargets().delete(
        id=self.request.get('id')).execute()
    return 'Share target has been deleted.'

  def _add_user_to_team(self):
    return "The users have been added to the team"

MAIN_ROUTES = [
    ('/', MainHandler)
]
