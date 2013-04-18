require 'rubygems'
require 'bundler'
require 'sinatra'
require 'omniauth'
require 'omniauth-google-oauth2'

require "./mira_mira.rb"

run MiraMira.new