class Alert

  attr_accessor :actions, :circle_names

  def initialize(alert_text, user)
    @alert_text = alert_text
    @user = user
    @circle_names = []
    @actions = []
  end

  def send
    body = self.construct_body
    @user.user_relations.where(:circles => {"$in" => @circle_names}).each do |rel|
      rel.recipient_user.timeline.insert(body)
    end
  end

  def construct_body
    {
        :notification => {:level => 'AUDIO_ONLY'},
        :text => @alert_text,
        :menu_items => @actions,
        :creator => creator
    }
  end

  def creator
    { :id => @user.uid, :display_name =>  @user.first_name, :image_urls => [@user.image]}
  end
end