class UserRelation
  include Mongoid::Document
  include Mongoid::Timestamps

  embedded_in :user

  field :circles, type: Array, :default => []
  belongs_to :recipient_user, :class_name => "User", :inverse_of => nil

  validates_presence_of :recipient_user
end