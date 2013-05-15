require "mirror-api"
require "hashie/mash"
require "mongoid"

require_relative "alert"
require_relative "../models/credential"
require_relative "../models/contact"
require_relative "../models/user"
require_relative "../models/user_relation"



class AppConfig

    class << self

    def environment
      rack_env = ENV['RACK_ENV']
      rack_env = rack_env.to_sym if rack_env.is_a?(String)
      rack_env || :development
    end

    def scope
      "userinfo.email,userinfo.profile,plus.me,https://www.googleapis.com/auth/glass.timeline,https://www.googleapis.com/auth/glass.location"
    end

    def key
      ENV['GOOGLE_KEY']
    end

    def secret
      ENV['GOOGLE_SECRET']
    end

    def configure_any_mongoid
      Mongoid.raise_not_found_error = false
      if ENV["MONGOLAB_URI"]
        configure_mongoid(ENV["MONGOLAB_URI"])
      else
        configure_mongoid_locally(environment)
      end
    end

    def configure_mongoid_locally(env)
      Mongoid.configure do |config|
        config.sessions = { :default => { :hosts => [ "localhost:27017" ], :database => "mira_mira_#{env}" }}
      end
    end

    def configure_mongoid(mongodb_url)
      Mongoid.configure do |config|
        config.sessions = { :default => { :uri => mongodb_url }}
      end
    end
  end

end