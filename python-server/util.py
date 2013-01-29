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

"""Utility functions for Starter Project."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import httplib2
from apiclient.discovery import build
from apiclient.discovery import build_from_document
from oauth2client.appengine import StorageByKeyName
import sessions
import json

from model import Credentials, User, UserCoords, CircleRelation


# Load the secret that is used for client side sessions
# Create one of these for yourself with, for example:
# python -c "import os; print os.urandom(64)" > session.secret
SESSION_SECRET = open('session.secret').read()


def load_session_credentials(request_handler):
  """Load credentials from the current session."""
  session = sessions.LilCookies(request_handler, SESSION_SECRET)
  userid = session.get_secure_cookie(name='userid')
  if userid:
    return userid, StorageByKeyName(Credentials, userid, 'credentials').get()
  else:
    return None, None


def store_userid(request_handler, userid):
  """Store current user's ID in session."""
  session = sessions.LilCookies(request_handler, SESSION_SECRET)
  session.set_secure_cookie(name='userid', value=userid)


def create_service(service, version, creds=None):
  """Create a Google API service.

  Load an API service from a discovery document and authorize it with the
  provided credentials.

  Args:
    service: Service name (e.g 'glass', 'oauth2').
    version: Service version (e.g 'v1').
    creds: Credentials used to authorize service.
  Returns:
    Authorized Google API service.
  """
  # Instantiate an Http instance
  http = httplib2.Http()

  if creds:
    # Authorize the Http instance with the passed credentials
    creds.authorize(http)

  # Build a service from the passed discovery document path
  if service == 'glass':
    return create_glass_service(http)
  else:
    return build(service, version, http=http)

def create_glass_service(http):
    discovery_file = open('glass.v1.json')
    result = build_from_document(discovery_file.read(), http=http)
    discovery_file.close()
    return result

def add_person_to_follow(follower, following, circleName):
  circleRelModel = None
  if following:
    for currentCircle in follower.circles:
      if currentCircle.name == circleName:
        circleRelModel = CircleRelation()
        circleRelModel.follower = follower.key()
        circleRelModel.following = following.key()
        circleRelModel.name = circleName
        circleRelModel.put()
  return circleRelModel

def add_person_to_follow_by_id(follower, following_id, circleName):
  following = User.get_by_key_name(following_id)
  add_person_to_follow(follower, following, circleName)
  return None

def auth_required(handler_method):
  """A decorator to require that the user has authorized the Glassware."""

  def check_auth(self, *args):
    self.userid, self.credentials = load_session_credentials(self)
    self.glass_service = create_service('glass', 'v1', self.credentials)
    # TODO(alainv): Also check that credentials are still valid.
    if not self.credentials:
      self.redirect('/auth')
      return
    else:
      userModel = User.get_by_key_name(self.userid)
      if userModel is None:
          http = httplib2.Http()
          self.credentials.authorize(http)
          _, content = http.request('https://www.googleapis.com/oauth2/v1/userinfo')
          userJson = json.loads(content)
          defaultCircles = ['Ops', 'Developers', 'QA', 'Bosses']
          userModel = User(
                 key_name=userJson['id'],
                 first_name=userJson['given_name'],
                 last_name=userJson['family_name'],
                 email=userJson['email'],
                 circles=defaultCircles,
                 photo=userJson['picture'])
          userModel.put()

      self.userModel = userModel
      handler_method(self, *args)
  return check_auth
