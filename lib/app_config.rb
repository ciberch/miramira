require "mirror-api"
require "hashie/mash"
require "mongoid"

require_relative "../models/credential"
require_relative "../models/contact"
require_relative "../models/circle"
require_relative "../models/user"


class AppConfig

  class << self

    def environment
      rack_env = ENV['RACK_ENV']
      rack_env = rack_env.to_sym if rack_env.is_a?(String)
      rack_env || :development
    end

    def configure_any_mongoid
      Mongoid.raise_not_found_error = false
      if ENV["MONGODB_URL"]
        configure_mongoid(ENV["MONGODB_URL"])
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
      puts "Configuring #{mongodb_url} ***"
      Mongoid.configure do |config|
        config.sessions = { :default => { :uri => mongodb_url }}
      end
    end
  end

end