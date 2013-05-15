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
    provider :google_oauth2, AppConfig.key, AppConfig.secret, {:scope => AppConfig.scope}

    # Custom scope supporting youtube
    # provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => 'http://gdata.youtube.com,userinfo.email,userinfo.profile,plus.me', :access_type => 'online', :approval_prompt => ''}
  end

  enable :sessions

  before do
    if session[:uid]
      @user = User.where(:uid => session[:uid]).first
    end
  end

  get '/' do
    @timeline_items = @user.timeline.list.items if @user
    erb :index
  end

  post '/alerts' do
    loc = nil

    if params[:lat] && params[:lng]
      loc = {:lat => params[:lat], :lng => params[:lng]}
    end

    if params[:remember]
      @user.location = loc if loc
      @user.phone_number = params[:phone_number] if params[:phone_number]
      @user.save!
    end

    @alert = Alert.new(
        {
            :sender => @user,
            :text => params[:message],
            :priority => params[:priority],
            :circles => params[:circles]
        }
    )
    @alert.phone_number = params[:phone_number] if params[:phone_number]
    @alert.location = loc if loc
    @alert.html = erb :alert, :layout => false
    @alert.save!
    redirect "/"
  end

  post '/users' do
    other = User.where(:uid => params[:member]).first
    name = params[:team]
    if other
      rel = @user.user_relations.where(:recipient_user_id => other.id).first

      if rel
        rel.circles << name unless rel.circles.is_a?(Array) && rel.circles.include?(name)
      else
        rel = UserRelation.new(:circles => [name], :recipient_user => other)
        puts "User Rel is #{rel.inspect}"
        @user.user_relations << rel if rel
      end
    end

    @user.save!
    redirect "/"
  end

  get '/signout' do
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
