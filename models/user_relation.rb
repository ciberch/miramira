class UserRelation
  include Mongoid::Document
  include Mongoid::Timestamps

  embedded_in :user

  field :circles, type: Array

  belongs_to :recipient_user, :class_name => "User"
end