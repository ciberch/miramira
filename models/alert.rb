class Alert
  include Mongoid::Document
  include Mongoid::Spacial::Document
  include Mongoid::Timestamps

  field :text
  field :html
  field :phone_number
  field :priority
  field :sent
  field :location, type: Array, spacial: true
  field :circles, :type => Array, :default => []
  field :recipients, :type => Array, :default => []

  belongs_to :sender, :class_name => "User", :inverse_of => :alerts_sent
  belongs_to :responder, :class_name => "User", :inverse_of => :alerts_handled

  before_create :insert_messages

  def insert_messages
    body = self.construct_body
    if location
      body[:location] = {:latitude => location[:lat], :longitude => location[:lng]}
      body[:menu_items] << { action: "NAVIGATE"}
    end
    if phone_number
      body[:creator][:phone_number] = phone_number
      body[:menu_items] << { action: "VOICE_CALL"}
    end
    rels = self.sender.user_relations.where(:circles => {"$in" => self.circles})
    if rels
      rels.each do |rel|
        resp = rel.recipient_user.timeline.insert(body)
        self.recipients << rel.recipient_user.id if resp
      end
      if self.recipients.count > 0
        self.sent = true
      end
    end
    puts "Saved alert #{self.inspect}"
  end


  def construct_body
    {
        :bundle_id => self._id,
        :notification => {:level => 'DEFAULT'},
        :text => self.text,
        :html => self.html,
        :menu_items => [{action: "REPLY"}, {action: "DELETE"}],
        :creator => creator
    }
  end

  def creator
    { :id => sender.uid, :display_name =>  sender.first_name, :image_urls => [sender.image]}
  end

  def color
    case priority
      when "High"
        "red"
      when "Medium"
        "yellow"
      else
        ""
    end
  end
end