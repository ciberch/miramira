class Circle
  include Mongoid::Document
  include Mongoid::Timestamps

  embedded_in :user

  field :name

  embeds_many :contacts, :as => :contactable
end