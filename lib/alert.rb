

class Alert
  def initialize(alert_text, user)
    @alert_text = alert_text
    @user = user
    @circles = []
    @actions = []
  end


  def withOptionTo(action)
    self.actions.append(action)
    self
  end

  def for_(circle)
    @circles << circle
  end

  def send
    body = self.construct_body
    @circles.each do |circle|
      body[:creator] = { :id => @user.id, :displayName =>  @user.first_name, :imageUrls => [@user.photo]}
      send_to_circle(body, circle)
    end
  end

  def send_to_circle(body, circle_name)
    circle = User.circles.where(:name => circle_name).first
    circle.peeps do |person|
      self.send_body(body, person)
    end
  end

  def send_body(body, user)
    client = Mirror::Api::Client.new(user.credentials.token)
    client.timeline.insert(body: body)
  end
end