import requests 
import urllib
import json
import sqlite3
import facebook 
import sys
import api_info
import datetime
import plotly
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

#By: Aidan Kearns



#load plotly credentials to log in they should be stored in api_info.py
plotly.tools.set_credentials_file(username=api_info.plotly_user, api_key=api_info.plotly_key) 

#Facebook API
FB_CACHE = "my_posts.json"
try:								#Try to open FB cache file
	cache_file = open(FB_CACHE,'r') 
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)

except:								#If file doesn't exist use GraphAPI to fetch data
	CACHE_DICTION = []
	access_token = api_info.fb_access_token
	graph = facebook.GraphAPI(access_token)
	all_fields = ['message', 'created_time', 'description', 'caption', 'link', 'place', 'status_type']
	all_fields = ','.join(all_fields)
	posts = graph.get_connections(id = 'me', connection_name = 'posts', fields = all_fields)
	while len(CACHE_DICTION) < 100:		#While loop to limit return to 100 interactions
		for post in posts['data']:
			if len(CACHE_DICTION) < 100:
				CACHE_DICTION.append(post)
		posts = requests.get(posts['paging']['next']).json()		#Go to next page until 100 interactions
	f = open('my_posts.json','w')
	f.write(json.dumps(CACHE_DICTION))
	f.close()
#Add FB Data to SQL
data = CACHE_DICTION
conn = sqlite3.connect('FacebookData.sqlite') #Connect to Database
cur = conn.cursor()
try: 
	cur.execute('SELECT id from Posts')
except:
	cur.execute('CREATE TABLE Posts (id TEXT, status_type TEXT, created_time TEXT)')
	for d in data:
		info = d["id"],d["status_type"],d["created_time"]
		cur.execute('INSERT INTO Posts (id, status_type, created_time) VALUES (?, ?, ?)', info)
conn.commit()
cur.close()

date = list()
for d in data:				#Get list of day of the week for each post
	x = d["created_time"]
	y = x.split('T')
	date.append(y[0])
day_of_week = list()
for d in date:
	l = d.split('-')
	day = datetime.datetime(int(l[0]),int(l[1]),int(l[2])).weekday()
	day_of_week.append(day)

def breakdown_day(day_of_week):
	#Arguments: list of days of the week each interaction took place
	#Returns: Dictionary with keys for each day of the week and values for number of interactions that took place on that day

	activity = {"Sunday":0,"Monday":0,"Tuesday":0,"Wednesday":0,"Thursday":0,"Friday":0,"Saturday":0}
	for d in day_of_week:
		if d == 6:
			activity["Sunday"] += 1
		if d == 0:
			activity["Monday"] += 1
		if d == 1:
			activity["Tuesday"] += 1
		if d == 2:
			activity["Wednesday"] += 1
		if d == 3:
			activity["Thursday"] += 1
		if d == 4:
			activity["Friday"] += 1
		if d == 5:
			activity["Saturday"] += 1
	return activity

print("Facebook Posts By Day")
print(breakdown_day(day_of_week))

time = list()	#Create list of time for each post
for d in data:
	x = d["created_time"]
	y = x.split('T')
	y = y[1]
	y = y.split('+')
	t = y[0]
	t = t.split(':')
	ti = t[0] + t[1]
	time.append(int(ti))
def breakdown_time(day_of_week,time):
	
	#Arguments: list of days of the week each interaction took place, list of time in (HHMM) integer format (24-hour clock format)
	#Returns: Dictionary with 28 keys, 4 six hour periods, 12:00am - 5:59am, 6:00am - 11:59pm, 12pm - 5:59 pm, and 6:00pm - 11:59pm, for all seven days, with the number of interactions that took place in each one
	
	activity_addon = {"Sunday 12:00am - 5:59am":0,"Sunday 6:00am - 11:59am":0,"Sunday 12:00pm - 5:59pm":0,"Sunday 6:00pm - 11:59pm":0,"Monday 12:00am - 5:59am":0,"Monday 6:00am - 11:59am":0,"Monday 12:00pm - 5:59pm":0,"Monday 6:00pm - 11:59pm":0,"Tuesday 12:00am - 5:59am":0,"Tuesday 6:00am - 11:59am":0,"Tuesday 12:00pm - 5:59pm":0,"Tuesday 6:00pm - 11:59pm":0,"Wednesday 12:00am - 5:59am":0,"Wednesday 6:00am - 11:59am":0,"Wednesday 12:00pm - 5:59pm":0,"Wednesday 6:00pm - 11:59pm":0,"Thursday 12:00am - 5:59am":0,"Thursday 6:00am - 11:59am":0,"Thursday 12:00pm - 5:59pm":0,"Thursday 6:00pm - 11:59pm":0,"Friday 12:00am - 5:59am":0,"Friday 6:00am - 11:59am":0,"Friday 12:00pm - 5:59pm":0,"Friday 6:00pm - 11:59pm":0,"Saturday 12:00am - 5:59am":0,"Saturday 6:00am - 11:59am":0,"Saturday 12:00pm - 5:59pm":0,"Saturday 6:00pm - 11:59pm":0}
	for c, t in enumerate(time):
		if day_of_week[c] == 6:
			if t >= 0 and t <= 559:
				activity_addon["Sunday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Sunday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Sunday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Sunday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 0:
			if t >= 0 and t <= 559:
				activity_addon["Monday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Monday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Monday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Monday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 1:
			if t >= 0 and t <= 559:
				activity_addon["Tuesday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Tuesday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Tuesday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Tuesday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 2:
			if t >= 0 and t <= 559:
				activity_addon["Wednesday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Wednesday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Wednesday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Wednesday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 3:
			if t >= 0 and t <= 559:
				activity_addon["Thursday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Thursday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Thursday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Thursday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 4:
			if t >= 0 and t <= 559:
				activity_addon["Friday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Friday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Friday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Friday 6:00pm - 11:59pm"] += 1
		if day_of_week[c] == 5:
			if t >= 0 and t <= 559:
				activity_addon["Saturday 12:00am - 5:59am"] += 1
			if t >= 600 and t <= 1159:
				activity_addon["Saturday 6:00am - 11:59am"] += 1
			if t >= 1200 and t <= 1759:
				activity_addon["Saturday 12:00pm - 5:59pm"] += 1
			if t >= 1800 and t <= 2359:
				activity_addon["Saturday 6:00pm - 11:59pm"] += 1
	return(activity_addon)
print("\n"+"Facebook Posts Add on B")
print(breakdown_time(day_of_week,time))


#Create pie chart of facebook posts by day using plotly
import plotly.plotly as py
import plotly.graph_objs as go

labels = list(breakdown_day(day_of_week).keys())
values = list(breakdown_day(day_of_week).values())
colors = ['rgb(127,0,255)', 'rgb(255,255,0)', 'rgb(255,0,0)', 'rgb(0,255,0)','rgb(0,0,255)','rgb(255,150,0)','rgb(20,255,255)']

trace = go.Pie(labels=labels, values=values,
              hoverinfo='label+percent', textinfo='value', 
             textfont=dict(size=20),
            marker=dict(colors=colors, 
                       line=dict(color='#000000', width=2)))
layout = go.Layout(title = 'Facebook Posts By Day')
fig = go.Figure(data=[trace],layout=layout)
py.plot(fig,filename='Facebook Posts By Day')


#Yelp API

def request(host, path, bearer_token, url_params=None):

	#Arguments: Yelp API host URL, API path after domain, Yelp private API key, and dictionary of URL parameters for a search
	#Returns: Dictionary of JSON response containing data from Yelp API request

    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()



def search(term,location):

	#Arguments: String of term to search Yelp for (EX: ‘Restaurants’), String of location for search
	#Returns: Dictionary of URL parameters for search term and location to be used as an argument in request()

	url_params = {
	'term': term.replace(' ', '+'),
	'location': location.replace(' ', '+'),
	'limit': 50
	}
	return (url_params)

YELP_CACHE_AA = 'yelpaa.json'
YELP_CACHE_EL = 'yelpel.json'
try:							#Check for Yelp Cache Files for Ann Arbor and East Lansing
    cache_file = open(YELP_CACHE_AA,'r')
    cache_file2 = open(YELP_CACHE_EL,'r') 
    cache_contents = cache_file.read()
    cache_contents2 = cache_file2.read()
    cache_file.close()
    cache_file2.close()
    CACHE_DICTION = json.loads(cache_contents)
    CACHE_DICTION2 = json.loads(cache_contents2)
except:							#If no Cache Fetch Data using functions defined above
	KEY = api_info.yelp_access_token
	API_HOST = 'https://api.yelp.com'
	SEARCH_PATH = '/v3/businesses/search'
	params = search('Restaurants','Ann Arbor')
	params2 = search('Restaurants','East Lansing')
	data = request(API_HOST, SEARCH_PATH, KEY, url_params=params)
	data2 = request(API_HOST, SEARCH_PATH, KEY, url_params=params2)
	CACHE_DICTION = data
	CACHE_DICTION2 = data2
	f = open(YELP_CACHE_AA,'w')
	f.write(json.dumps(CACHE_DICTION))
	f.close()
	f = open(YELP_CACHE_EL,'w')
	f.write(json.dumps(CACHE_DICTION2))
	f.close()
data = CACHE_DICTION["businesses"]		#JSON Format, data of interest is listed under businesses
data2 = CACHE_DICTION2["businesses"]


conn = sqlite3.connect('Yelp.sqlite') #Connect to Database
cur = conn.cursor()
try:
	cur.execute('SELECT name from YELP')
except:
	cur.execute('CREATE TABLE Yelp (name TEXT, price TEXT, rating NUMBER, city TEXT, id TEXT)')

	for d in data:
		info = d["name"],d["price"],d["rating"],d["location"]["city"],d["id"]
		cur.execute('INSERT INTO Yelp (name, price, rating, city, id) VALUES (?, ?, ?, ?, ?)', info)
	for d in data2:
		try:			#Not all East Lansing Restuarants have prices so we must use a try except in case of error
			info = d["name"],d["price"],d["rating"],d["location"]["city"],d["id"]
			cur.execute('INSERT INTO Yelp (name, price, rating, city, id) VALUES (?, ?, ?, ?, ?)', info)
		except:
			info = d["name"],"NA",d["rating"],d["location"]["city"],d["id"]
			cur.execute('INSERT INTO Yelp (name, price, rating, city, id) VALUES (?, ?, ?, ?, ?)', info)
conn.commit()
cur.close()

aa_rating = list()
for d in data:		#List of Ann Arbor and East Lansing Ratings
	aa_rating.append(d["rating"])
el_rating = list()
for d in data2:
	el_rating.append(d["rating"])
rating = aa_rating+el_rating
def breakdown_ratings(rating):

	#Arguments: list of Yelp rating for each restaurant
	#Returns: Dictionary with keys of each possible rating and values of number of restaurants with each rating

	ratings = {"0":0,"0.5":0,"1":0,"1.5":0,"2":0,"2.5":0,"3":0,"3.5":0,"4":0,"4.5":0,"5":0}
	for r in rating:
		if r == 0:
			ratings["0"] += 1
		if r == 0.5:
			ratings["0.5"] += 1
		if r == 1:
			ratings["1"] += 1	
		if r == 1.5:
			ratings["1.5"] += 1
		if r == 2:
			ratings["2"] += 1
		if r == 2.5:
			ratings["2.5"] += 1
		if r == 3:
			ratings["3"] += 1
		if r == 3.5:
			ratings["3.5"] += 1
		if r == 4:
			ratings["4"] += 1
		if r == 4.5:
			ratings["4.5"] += 1
		if r == 5:
			ratings["5"] += 1
	return(ratings)
print("\n"+"Restaurants by Yelp Rating")
print(breakdown_ratings(rating))


aa = breakdown_ratings(aa_rating)
el = breakdown_ratings(el_rating)

#Create bar char using plotly that compares ratings in Ann Arbor to East Lansing

trace1 = go.Bar(
   x=list(aa.keys()),
  y=list(aa.values()),
   name='Ann Arbor',
   marker = dict(color='rgb(0,0,255)')
)
trace2 = go.Bar(
  x=list(el.keys()),
    y=list(el.values()),
     name='East Lansing',
     marker = dict(color ='rgb(0,51,0)')
)

plotdata = [trace1, trace2]
layout = go.Layout(
  barmode='group',title='Restaurant Yelp Ratings Ann Arbor vs East Lansing',xaxis=dict(title='Yelp Rating'),yaxis=dict(title='Number of Restaurants')
)

fig = go.Figure(data=plotdata, layout=layout)
py.plot(fig, filename='Restaurant Yelp Ratings Ann Arbor vs East Lansing')

#Fetch price and rating data from database
conn = sqlite3.connect('Yelp.sqlite')
cur = conn.cursor()
cur.execute('SELECT price, rating FROM Yelp')
results = cur.fetchall()
cur.close()

#Create rating breakdown dictionaries for each price group
four = list()
for tup in results:
	if tup[0] == '$$$$':
		four.append(tup[1])
three = list()
for tup in results:
	if tup[0] == '$$$':
		three.append(tup[1])
two = list()
for tup in results:
	if tup[0] == '$$':
		two.append(tup[1])
one = list()
for tup in results:
	if tup[0] == '$':
		one.append(tup[1])
ones = breakdown_ratings(one)
twos = breakdown_ratings(two)
threes = breakdown_ratings(three)
fours = breakdown_ratings(four)
print("\n" + "Yelp Rating By Price (Add on B)")
print("$",ones)
print("$$",twos)
print("$$$",threes)
print("$$$$",fours)


#Create stacked bar chart comparing ratings across price groups
trace1 = go.Bar(
   x=list(ones.keys()),
     y=list(ones.values()),
      name='$',
      marker = dict(color='rgb(0,0,255)')
)
trace2 = go.Bar(
   x=list(twos.keys()),
     y=list(twos.values()),
       name='$$',
         marker = dict(color ='rgb(255,0,0)')
)
trace3 = go.Bar(
   x=list(threes.keys()),
     y=list(threes.values()),
       name='$$$',
       marker = dict(color='rgb(0,255,51)')
)
trace4 = go.Bar(
   x=list(fours.keys()),  
   y=list(fours.values()),
   name='$$$$',
   marker = dict(color ='rgb(255,0,127)')
)

plotdata = [trace1, trace2,trace3,trace4]
layout = go.Layout(
   barmode='stack',title='Restaurant Yelp Ratings By Price',xaxis=dict(title='Yelp Rating'),yaxis=dict(title='Number of Restaurants')
)

fig = go.Figure(data=plotdata, layout=layout)
py.plot(fig, filename='Restaurant Yelp Ratings By Price')




#GitHub API
sys.path.append("./PyGithub");
from github import Github

GITHUB_CACHE = 'github.json'
try:					#Get data from GitHub Cache
	cache_file = open(GITHUB_CACHE,'r') 
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:			#Fetch Data using PyGitHub library if no cache
	username = api_info.git_user
	pw = api_info.git_pass
	g = Github(username, pw)#Authenticate User
	data = g.get_user().get_repos()#Get user repositories
	CACHE_DICTION = []
	for d in data:
		info = {"id": d.id, "name": d.name,"size": d.size, "created_at": str(d.created_at)}
		CACHE_DICTION.append(info)
	f = open(GITHUB_CACHE,'w')
	f.write(json.dumps(CACHE_DICTION))
	f.close()

data = CACHE_DICTION
conn = sqlite3.connect('Github.sqlite') #Connect to Database
cur = conn.cursor()
try:
	cur.execute('SELECT id FROM Repo')
except:
	cur.execute('CREATE TABLE Repo (id NUMBER, name TEXT, size NUMBER, created_at TIMESTAMP)')
	for d in data:
		info = d["id"],d["name"],d["size"],d["created_at"]
		cur.execute('INSERT INTO Repo (id, name, size, created_at) VALUES (?, ?, ?, ? )', info)
conn.commit()
cur.close()


date = list()
for d in data:		#List of dates repos were made
	x = d["created_at"]
	y = x.split(' ')
	date.append(y[0])
day_of_week = list()
for d in date:		#List of days repos were made
	l = d.split('-')
	day = datetime.datetime(int(l[0]),int(l[1]),int(l[2])).weekday()
	day_of_week.append(day)
#Day breakdown for repos
print("\n" + "GitHub Repositories By Day")
print(breakdown_day(day_of_week))

time = list()
for d in data:	#List of times repos were made
	x = d["created_at"]
	y = x.split(' ')
	y = y[1]
	t = y.split(':')
	ti = t[0] + t[1]
	time.append(int(ti))

#Add on B Day/Time breakdown 
print("\n"+"GitHub Repositories Add on B")
print(breakdown_time(day_of_week,time))



#New York Times API
url = "https://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/30.json"
url += '?'  + "api-key=ab3c4868ee84417f8ddb8fecdde40f80"
r = requests.get(url)
data = r.json()
NYT_CACHE = "nyt.json"
try:					#Try NYT Cache
    cache_file = open(NYT_CACHE,'r') 
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:					#If no cache dump into new cache using requests library to fetch data
    CACHE_DICTION = data
    f = open(NYT_CACHE,'w')
    f.write(json.dumps(CACHE_DICTION))
    f.close()

conn = sqlite3.connect('NYT.sqlite') #Connect to Database
cur = conn.cursor()
try:
	cur.execute('SELECT title FROM NYT')
except:
	data_sql = data["results"]
	cur.execute('CREATE TABLE NYT (title TEXT, published_date TEXT, section TEXT, id NUMBER)')
	for d in data_sql:
		info = d["title"],d["published_date"],d["section"],d["id"]
		cur.execute('INSERT INTO NYT (title, published_date, section, id) VALUES (?, ?, ?, ? )', info)

#Fetch date and section from SQL Database
cur.execute('SELECT published_date, section FROM NYT')
results = cur.fetchall()
day_of_week = list()
conn.commit()
cur.close()
for r in results:	#Create list of days articles were published
	x = r[0]
	l = x.split('-')
	day = datetime.datetime(int(l[0]),int(l[1]),int(l[2])).weekday()
	day_of_week.append(day)
print("\n" + "Most Viewed Articles By Day Published")
print(breakdown_day(day_of_week))

sections = list()
for r in results:		#Create list of sections articles are in 
	sections.append(r[1])
results = list(zip(day_of_week,sections))	#Create list of tupples for day of week and section for each article
sect = set(sections)		#Unique sections
print("\n" + "Article Day By Section (Add on B)")
for s in sect:		#Break down each section by articles published on each day
	days_by_section = list()
	for res in results:
		if res[1] == s:
			days_by_section.append(res[0])
	print(s, breakdown_day(days_by_section))













