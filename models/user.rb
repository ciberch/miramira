class User
  include Mongoid::Document
  include Mongoid::Timestamps

  field :uid
  field :circles, type: Array, :default => ["developers", "explorers", "family", "team", "fans"]

  embeds_one :contact, :as => :contactable
  embeds_one :credential

  embeds_many :user_relations
  has_many :alerts_sent, :class_name => "Alert", :inverse_of => :sender
  has_many :alerts_handled, :class_name => "Alert", :inverse_of => :responder

  delegate :image, :to => :contact
  delegate :name, :to => :contact
  delegate :first_name, :to => :contact

  public

  def get_others
    User.all
  end

  def timeline
    client.timeline
  end

  def client
    @client ||= Mirror::Api::Client.new(credential.to_hash)
  end
end