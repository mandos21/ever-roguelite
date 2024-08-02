require 'bundler/setup'
Bundler.require(:default, ENV['RACK_ENV'] || :development)

require 'dotenv/load'

Mongoid.load!(File.join(File.dirname(__FILE__), 'mongoid.yml'))

Dir[File.join(__dir__, '../app/**/*.rb')].each { |file| require file}


ZMQ_CONTEXT = ZMQ::Context.new
