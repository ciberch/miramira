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

"""OAuth 2.0 handlers."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import logging
import webapp2
from urlparse import urlparse

from oauth2client.appengine import StorageByKeyName
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from model import Credentials
import util


SCOPES = ('https://www.googleapis.com/auth/glass.timeline '
          'https://www.googleapis.com/auth/userinfo.email '
          'https://www.googleapis.com/auth/userinfo.profile')


class OAuthBaseRequestHandler(webapp2.RequestHandler):
  """Base request handler for OAuth 2.0 flow."""

  def create_oauth_flow(self):
    """Create OAuth2.0 flow controller."""
    flow = flow_from_clientsecrets('client_secrets.json', scope=SCOPES)
    # Dynamically set the redirect_uri based on the request URL. This is extremely
    # convenient for debugging to an alternative host without manually setting the
    # redirect URI.
    pr = urlparse(self.request.url)
    flow.redirect_uri = '%s://%s/oauth2callback' % (pr.scheme, pr.netloc)
    return flow


class OAuthCodeRequestHandler(OAuthBaseRequestHandler):
  """Request handler for OAuth 2.0 auth request."""

  def get(self):
    flow = self.create_oauth_flow()
    flow.params['approval_prompt'] = 'force'
    # Create the redirect URI by performing step 1 of the OAuth 2.0 web server
    # flow.
    uri = flow.step1_get_authorize_url()
    # Perform the redirect.
    self.redirect(str(uri))


class OAuthCodeExchangeHandler(OAuthBaseRequestHandler):
  """Request handler for OAuth 2.0 code exchange."""

  def get(self):
    """Handle code exchange."""
    code = self.request.get('code')
    if not code:
      # TODO(alainv): Display error.
      return None
    oauth_flow = self.create_oauth_flow()

    # Perform the exchange of the code. If there is a failure with exchanging
    # the code, return None.
    try:
      creds = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
      # TODO(alainv): Display error.
      return None

    users_service = util.create_service('oauth2', 'v2', creds)
    # TODO(alainv): Check for errors.
    user = users_service.userinfo().get().execute()

    userid = user.get('id')

    # Store the credentials in the data store using the userid as the key.
    # TODO(alainv): Hash the userid the same way the verify token is.
    StorageByKeyName(Credentials, userid, 'credentials').put(creds)
    logging.info('Successfully stored credentials for user: %s', userid)
    util.store_userid(self, userid)

    self.redirect('/')


OAUTH_ROUTES = [
    ('/auth', OAuthCodeRequestHandler),
    ('/oauth2callback', OAuthCodeExchangeHandler)
]