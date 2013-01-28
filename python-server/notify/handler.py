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

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import json
import logging
import webapp2

from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    data = json.loads(self.request.body)
    userid = data['userToken']
    glass_service = util.create_service(
        'glass', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())

    # Fetch the timeline item.
    item = glass_service.timeline().get(id=data['itemId']).execute()
    logging.info(
        'Got a notification with payload %s that impacted timeline item with ' +
        'ID: %s', self.request.body, item.get('id'))

    attachments = item.get('attachments', [])
    media = None
    if attachments:
      # Get the first attachment on that timeline item and do stuff with it.
      attachment = glass_service.attachments().get(
          itemId=data['itemId'], attachmentId=attachments[0]['id']).execute()
      media = MediaIoBaseUpload(
          io.BytesIO(attachment), attachments[0]['contentType'], resumable=True)
    body = {
        'text': 'Echoing your shared item: %s' % item.get('text', ''),
        'notification': {'level': 'AUDIO_ONLY'}
    }
    glass_service.timeline().insert(body=body, media_body=media).execute()


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
