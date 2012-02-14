#! /usr/bin/env python3

from datetime import datetime
import time
import urllib.parse
import urllib.request
import re
import os

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

def requestPunch(type, cookie):
	if type == PUNCHIN:
		print("Performing 'Punch in' ...")
	elif type == PUNCHOUT:
		print("Performing 'Punch out' ...")
	
	url = 'http://74.208.197.154:8085/interface/punch/Punch.php'

	user_id = getUserId(cookie)
	dt_now = datetime.now()
	#dt_now = datetime(2012, 2, 7, 8, 2, 9, 465714)
	timestamp = int((time.mktime(dt_now.timetuple()) + dt_now.microsecond/1000000.0)*1000)
	values = {
		'data[time_stamp]'     : timestamp,
		'data[type_id]' : '10',
		'data[status_id]' : type,
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

def getCurrentCredintials():
	try:
		userHomeDir = os.path.expanduser("~")
		config = open("{}/.punchConfig".format(userHomeDir), 'r')
	except IOError:
		return None, None
	configuration = config.readlines()
	config.close()
	username = configuration[0][:-1]	#remove the endline character from the first line
	password = configuration[1]
	return username, password

def writeCredintials(username, password):
	userHomeDir = os.path.expanduser("~")
	config = open("{}/.punchConfig".format(userHomeDir), 'w')
	config.write("{}\n{}".format(username, password))
	config.close()
	return

def punch(type, username, password):
	try:
		response = login(username, password)
		if response is None:
			print("\n**Failure**")
			return
		cookie = extractCookie(response)
		requestPunch(type, cookie)
		print("\n**Success!**")
	except urllib.error.HTTPError as e:
		print("\n**Failure**")
		return
	except KeyboardInterrupt:
		print("")
		print("Aborted by user.")
	return

####################################################################################################
# Bigining of the execution
####################################################################################################
print(" -----------------")
print("| version: 0.9    |")
print("| author: kdehairy|")
print(" -----------------")

#set default values for the global variables
currentUsername, currentPassword = (None, None)

#get the current username and password if any
currentUsername, currentPassword = getCurrentCredintials()
if currentUsername is None:
	currentUsername = "not set"

while True:
	print("\n\n1. punchIn.")
	print("2. PunchOut")
	print("3. Set username and password (current username: '{}').".format(currentUsername))
	print("4. Exit")
	choice = input("Enter a choice (1 to 4, default 1) : ")
	if choice == "":
		choice = "0"
	try:
		if int(choice) not in range(0,5):
			print("invalid choice. please choose a number between 1 and 4")
			continue
	except ValueError:
		print("invalid choice. please choose a number between 1 and 4")
		continue
	
	if choice == "1" or choice == "0":
		if currentPassword is None:
			currentUsername = input("username: ")
			currentPassword = input("password: ")
		punch(PUNCHIN, currentUsername, currentPassword)
	elif choice == "2":
		if currentPassword is None:
			currentUsername = input("username: ")
			currentPassword = input("password: ")
		punch(PUNCHOUT, currentUsername, currentPassword)
	elif choice == "3":
		currentUsername = input("username: ")
		currentPassword = input("password: ")
		writeCredintials(currentUsername, currentPassword)
	elif choice == "4":
		exit(0)

	
		