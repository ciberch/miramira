class Contact
  include Mongoid::Document

  embedded_in :contactable, polymorphic: true

  field :name
  field :first_name
  field :last_name
  field :email
  field :image
end