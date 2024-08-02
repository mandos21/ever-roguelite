require 'rspec'
require 'rack/test'
require File.expand_path '../../config/environment.rb', __FILE__

ENV['RACK_TEST'] ||= 'test'


RSpec.configure do |config|
  config.include Rack::Test::Methods

  config.include Mongoid::Matchers

  def app
    Sinatra::Application
  end

  config.before(:suite) do
    Mongoid.purge! # Clean database before tests
  end

  config.after(:each) do
    Mongoid.purge! # Clean database after each test
  end
end
