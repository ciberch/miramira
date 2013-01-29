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

from model import Credentials, User
import util


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    data = json.loads(self.request.body)
    userid = data['userToken']
    username = User.get_by_key_name(userid).first_name
    collection = data['collection']
    TOKEN = data.get('verifyToken')
    if TOKEN:
       logging.info('Token is here as expected?')
    else:
       logging.info('Do not know where this came from, but assuming its us')

    if collection != 'timeline':
       logging.info('Got a non timeline reply %s' % collection)
       return
    
    glass_service = util.create_service(
        'glass', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())

    # Fetch the timeline item.
    logging.info('data[%s]' % json.dumps(data))
    reply_item = glass_service.timeline().get(id=data['itemId']).execute()

    logging.info(
        'Got a notification with payload %s that impacted timeline item with ' +
        'ID: %s\n RESPONSE %s', self.request.body, reply_item.get('inReplyTo'), json.dumps(reply_item))

    operation = data['operation']
    if operation != 'INSERT':
        logging.info('Ignoring non insert operation, %s' % operation)
        return 

    reply_text = reply_item.get('text')
    original_post = glass_service.timeline().get(id=reply_item.get('inReplyTo', '')).execute()
    original_post['text'] = 'Being Handled by %s:\n%s' % (username, original_post['text'])
    glass_service.timeline().update(id=original_post['id'], body=original_post).execute()
    glass_service.timeline().delete(timelineId=reply_item['id']).execute()


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
