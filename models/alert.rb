class Alert
  include Mongoid::Document
  include Mongoid::Timestamps

  field :text
  field :priority
  field :sent
  field :circles, :type => Array, :default => []
  field :recipients, :type => Array, :default => []

  belongs_to :sender, :class_name => "User", :inverse_of => :alerts_sent
  belongs_to :responder, :class_name => "User", :inverse_of => :alerts_handled

  before_create :insert_messages

  def insert_messages
    body = self.construct_body
    rels = self.sender.user_relations.where(:circles => self.circles)
    rels.each do |rel|
      rel.recipient_user.timeline.insert(body)
      self.recipients << rel.recipient_user.id
    end
    if self.recipients.count > 0
      self.sent = true
    end
  end

  def construct_body
    {
        :notification => {:level => 'AUDIO_ONLY'},
        :text => self.text,
        :menu_items => [{action: "REPLY"}],
        :creator => creator
    }
  end

  def creator
    { :id => sender.uid, :display_name =>  sender.first_name, :image_urls => [sender.image]}
  end
end