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


import webapp2

from apiclient.model import MediaModel

from util import auth_required


class ContentTypeModel(MediaModel):
  """Inherits from MediaModel to host an additional content_type attribute."""

  def __init__(self, *args, **kwargs):
    """Construct a new ContentTypeModel."""
    MediaModel.__init__(self, *args, **kwargs)
    self.content_type = None

  def response(self, resp, content):
    """Store the content-type and call the original response."""
    for key, value in resp.iteritems():
      if key.lower() == 'content-type':
        self.content_type = value
        break
    return MediaModel.response(self, resp, content)


class AttachmentProxyHandler(webapp2.RequestHandler):
  """Request Handler for the main endpoint."""

  @auth_required
  def get(self):
    """Return the attachment's content using the current user's credentials."""
    # self.glass_service is initialized in util.auth_required.
    attachment_id = self.request.get('attachment')
    item_id = self.request.get('timelineItem')
    if not attachment_id or not item_id:
      self.response.set_status(400)
      return
    else:
      request = self.glass_service.attachments().get_media(
          itemId=item_id, attachmentId=attachment_id)
      cm = ContentTypeModel()
      request.postproc = cm.response
      attachment = request.execute()
      self.response.headers.add_header('Content-type', cm.content_type)
      self.response.out.write(attachment)


ATTACHMENT_PROXY_ROUTES = [
    ('/attachmentproxy', AttachmentProxyHandler)
]
