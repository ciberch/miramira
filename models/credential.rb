class Credential
  include Mongoid::Document

  embedded_in :user

  field :token
  field :refresh_token

  field :expires, type: Boolean
  field :expires_at, type: DateTime

  def to_hash
    {
        :token => token,
        :refresh_token => refresh_token
    }
  end
end