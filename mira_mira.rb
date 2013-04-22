OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE

require "mirror-api"

class MiraMira < Sinatra::Base

  use Rack::Session::Cookie, :secret => ENV['RACK_COOKIE_SECRET']

  configure do
    set :views, "#{File.dirname(__FILE__)}/views"
  end

  use OmniAuth::Builder do
    # Regular usage
    provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => "userinfo.email,userinfo.profile,plus.me,https://www.googleapis.com/auth/glass.timeline,https://www.googleapis.com/auth/glass.location"}

    # Custom scope supporting youtube
    # provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => 'http://gdata.youtube.com,userinfo.email,userinfo.profile,plus.me', :access_type => 'online', :approval_prompt => ''}
  end

  enable :sessions

  get '/' do
    erb :index
  end


  get '/auth/:provider/callback' do
    content_type 'application/json'
    session[:info] = request.env['omniauth.auth']['info']
    session[:credentials] = request.env['omniauth.auth']['credentials']
    redirect "/"
  end

  get '/auth/failure' do
    content_type 'text/plain'
    session[:credentials] = nil
    redirect "/"
  end
end
