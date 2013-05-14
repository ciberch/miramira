OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE

require_relative "lib/app_config"

class MiraMira < Sinatra::Base

  configure do
    set :views, "#{File.dirname(__FILE__)}/views"
  end

  def initialize
    super
    AppConfig.configure_any_mongoid
  end

  use OmniAuth::Builder do
    # Regular usage
    provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => "userinfo.email,userinfo.profile,plus.me,https://www.googleapis.com/auth/glass.timeline,https://www.googleapis.com/auth/glass.location"}

    # Custom scope supporting youtube
    # provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => 'http://gdata.youtube.com,userinfo.email,userinfo.profile,plus.me', :access_type => 'online', :approval_prompt => ''}
  end

  enable :sessions

  before do
    if session[:uid]
      @user = User.where(:uid => session[:uid]).first
      @client = Mirror::Api::Client.new(@user.credential.token) if @user
    end
  end

  get '/' do
    @timeline_items = @client.timeline.list.items if @client
    erb :index
  end

  post '/team_send' do
    msg = params[:message]
    if msg
      priority = params[:priority]

      file = params[:file]
      if file
        @client.timeline.insert({text: msg}, file)
      else
        @client.timeline.insert(text: msg)
      end

    end
    redirect "/"
  end

  get '/logout' do
    session[:uid] = nil
    "You are logged out"
  end

  get '/auth/:provider/callback' do
    uid = request.env['omniauth.auth']['uid']

    if uid
      user = User.find_or_initialize_by(:uid => uid)
      if user
        user.contact = Contact.new(request.env['omniauth.auth']['info'])
        user.credential = Credential.new(request.env['omniauth.auth']['credentials'])
        user.save!
      end

      session[:uid] = uid
    end

    redirect "/"
  end

  get '/auth/failure' do
    content_type 'text/plain'
    session[:uid] = nil
    redirect "/"
  end
end
