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

"""Datastore models for Starter Project"""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


from google.appengine.ext import db

from oauth2client.appengine import CredentialsProperty


class Credentials(db.Model):
  """Datastore entity for storing OAuth2.0 credentials.

  The CredentialsProperty is provided by the Google API Python Client, and is
  used by the Storage classes to store OAuth 2.0 credentials in the data store.
  """
  credentials = CredentialsProperty()

class User(db.Model):
  first_name = db.StringProperty()
  last_name = db.StringProperty()
  email = db.StringProperty()
  photo = db.LinkProperty()
  circles = db.StringListProperty()

class UserCoords(db.Model):
  user = db.ReferenceProperty(User)
  latitude = db.FloatProperty()
  longitude = db.FloatProperty()
  created_at = db.DateProperty()

class CircleRelation(db.Model):
  name = db.StringProperty()
  follower = db.ReferenceProperty(User)
  following = db.ReferenceProperty(User) 

