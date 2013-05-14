class Credential
  include Mongoid::Document

  embedded_in :user

  field :token
  field :refresh_token

  field :expires, type: Boolean
  field :expires_at, type: DateTime
end