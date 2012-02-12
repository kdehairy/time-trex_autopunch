#! /usr/bin/env python3

from datetime import datetime
import time
import urllib.parse
import urllib.request
import re

PUNCHIN = "10"
PUNCHOUT = "20"

def extractCookie(response):
	cookie = ""
	for header,value in response.headers.items():
		if header == "Set-Cookie":
			cookie += value + "; "
	cookie = cookie[:-2]
	return cookie

def getUserId(cookie):
	url = 'http://74.208.197.154:8085/interface/punch/Punch.php'
	headers = {
		#'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7',
		'Accept'     : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset' : 'utf-8',
		'Content-Type' : 'application/x-www-form-urlencoded',
		'Host' : '74.208.197.154:8085',
		#'Origin' : 'http://74.208.197.154:8085',
		'Referer' : 'http://74.208.197.154:8085/interface/Login.php',
		#'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8',
		'Cache-Control' : 'max-age=0',
		'Connection' : 'keep-alive',
		'Cookie' : cookie
	}
	request = urllib.request.Request(url, headers=headers)
	user_id = ""
	try:
		response = urllib.request.urlopen(request)
		html_str = str(response.read())
		patern = re.compile(r'<input type="hidden" name="data\[user_id\]" value="(\d+)">', re.IGNORECASE)
		#print(html_str)
		match = patern.search(html_str)
		if (match):
			user_id = match.group(1)
	except Exception:
		raise
		return ""
	return user_id

def punchIn(cookie):
	print("Performing 'Punch in' ...")
	url = 'http://74.208.197.154:8085/interface/punch/Punch.php'

	user_id = getUserId(cookie)
	dt_now = datetime.now()
	#dt_now = datetime(2012, 2, 7, 8, 2, 9, 465714)
	timestamp = int((time.mktime(dt_now.timetuple()) + dt_now.microsecond/1000000.0)*1000)
	values = {
		'data[time_stamp]'     : timestamp,
		'data[type_id]' : '10',
		'data[status_id]' : PUNCHIN,
		'data[branch_id]' : '1',
		'data[department_id]' : '4',
		'data[user_id]' : user_id,
		'data[note]' : 'This an automatic punch in',
		'action:submit' : 'Submit'
	}
	headers = {
		#'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7',
		'Accept'     : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset' : 'utf-8',
		'Content-Type' : 'application/x-www-form-urlencoded',
		'Host' : '74.208.197.154:8085',
		#'Origin' : 'http://74.208.197.154:8085',
		'Referer' : 'http://74.208.197.154:8085/interface/Login.php',
		#'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8',
		'Cache-Control' : 'max-age=0',
		'Connection' : 'keep-alive',
		'Cookie' : cookie
	}
	data = urllib.parse.urlencode(values)
	data = data.encode('utf-8')
	request = urllib.request.Request(url, data, headers)
	response = None
	try:
		#response = opener.open(request)
		response = urllib.request.urlopen(request)
		#fancyOpener = urllib.request.FancyURLopener()
		#fancyOpener.addheader(**headers)
		#response = fancyOpener.open(url, data)
	except urllib.error.HTTPError as e:
		if e.code == 302:
			response = e
		else:
			print("Punch in failed")
			raise
	return response

def login(username, password):
	print("Logging in as '{}' ...".format(username))
	url = 'http://74.208.197.154:8085/interface/login.php'
	values = {
		'user_name'     : username,
		'password'      : password,
		'language'      : 'en',
		'action:submit' : 'Submit'
	}
	headers = {
		#'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7',
		'Accept'     : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset' : 'utf-8',
		'Content-Type' : 'application/x-www-form-urlencoded',
		'Host' : '74.208.197.154:8085',
		#'Origin' : 'http://74.208.197.154:8085',
		'Referer' : 'http://74.208.197.154:8085/interface/Login.php',
		#'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8',
		'Cache-Control' : 'max-age=0',
		'Connection' : 'keep-alive'
	}
	data = urllib.parse.urlencode(values)
	data = data.encode('utf-8')
	request = urllib.request.Request(url, data, headers)
	response = None
	try:
		response = urllib.request.urlopen(request)
		if response.code == 200:
			print("Login failed.")
			return None
	except urllib.error.HTTPError as e:
		print(e.code)
		if e.code == 302:
			response = e
		else:
			print("Login failed.")
			raise
	return response

####################################################################################################
print(" -----------------")
print("| version: 0.8    |")
print("| author: kdehairy|")
print(" -----------------")
cookie = ""
response = None
try:
	username = input("username: ")
	password = input("password: ")
	response = login(username, password)
	if response is None:
		print("Failure")
		exit()
	cookie = extractCookie(response)
	punchIn(cookie)
	print("Success!")
except urllib.error.HTTPError as e:
	print("Failure")
	exit()
except KeyboardInterrupt:
	print("")
	print("Aborted by user.")
	exit()
		