OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE

class MiraMira < Sinatra::Base

  use Rack::Session::Cookie, :secret => ENV['RACK_COOKIE_SECRET']

  use OmniAuth::Builder do
    # Regular usage
    provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => "userinfo.email,userinfo.profile,plus.me,https://www.googleapis.com/auth/glass.timeline"}

    # Custom scope supporting youtube
    # provider :google_oauth2, ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {:scope => 'http://gdata.youtube.com,userinfo.email,userinfo.profile,plus.me', :access_type => 'online', :approval_prompt => ''}
  end

  enable :sessions

  get '/' do
    <<-HTML
    <ul>
      <li><a href='/auth/google_oauth2'>Sign in with Google</a></li>
    </ul>
    HTML
  end

  get '/auth/:provider/callback' do
    content_type 'application/json'
    request.env['omniauth.auth'].to_json rescue "No Data"
  end

  get '/auth/failure' do
    content_type 'text/plain'
    request.env['omniauth.auth'].to_hash.inspect rescue "No Data"
  end
end
