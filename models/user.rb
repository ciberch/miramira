class User
  include Mongoid::Document
  include Mongoid::Timestamps

  field :uid

  embeds_one :contact, :as => :contactable
  embeds_one :credential

  embeds_many :circles

  delegate :image, :to => :contact
  delegate :name, :to => :contact
  delegate :first_name, :to => :contact

  public

  def get_others
    User.all
  end
end