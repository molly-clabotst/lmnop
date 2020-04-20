import requests
from django.http import HttpResponse
from django.db import IntegrityError
from django.db import models



event_url = 'https://app.ticketmaster.com/discovery/v2/events'
venue_url = 'https://app.ticketmaster.com/discovery/v2/venues'
  
key = '7CyQJ1JxlnqGBJe0uEkZw9h8SMvjoLQ9'


def get_data(requests):
        try:
                artist_list()
                venue_list()
                show_list()
                return HttpResponse('ok')
                # gettign artist, venues and shows and providing an httpresponse if successful
        except Exception as e:
                print(e)
                return HttpResponse('failed')
def artist_list():
    
    url = 'https://app.ticketmaster.com/discovery/v2/events.json?classificationName=music&stateCode=MN&apikey=7CyQJ1JxlnqGBJe0uEkZw9h8SMvjoLQ9'
    artist_names = [] # Empty list to hold all the artist output, using this to make sure check for duplicate entries.
    try:
        data = requests.get(url).json() # api call for 'music' events with the statecode 'MN'
        events = data['_embedded']['events']
        for event in events: # Cycles through the JSON and finds the event names, Better to use a for than a range, take note of that. 
            artist_name = event['name']
            if artist_name not in artist_names: # Makes sure there are no duplicates. 
                new_artist=Artist(name=artist_name)
                new_artist.save()
                artist_names.append(artist_name) # adds artist to list for filtering
                print(artist_name)

            else:
                print('already added') # Maybe put something more meaningful here?
    except Exception as e:
        print(e)
def venue_list():

    query = {'apikey': key , 'stateCode' : 'MN', 'name' : 'music'}
    venues_names = [] # Create an empty list to store previously created venues.
    try:
        data = requests.get(venue_url, params=query).json() # Retrives a JSON from ticketmaster
        venues = data['_embedded']['venues']
        for venue in venues: # finds each venue in the json response
            venues_names += venue # adds the venues to a list 
            if venue not in venues_names: # checks for duplicates of venues 
                venue_name = venue['name'] # assigning a variable to the venue_name
                venue_city = venue['city']['name'] # finding value for the venue city
                venue_state = venue['state']['name'] # assigning value for the venue state
                venue_new = Venue(name= venue_name, city= venue_city, state=venue_state) # creates a .models/Venue object and assigns the values
                venue_new.save() # Saves the object into the database
                print(venue_name,venue_city,venue_state)


    except IntegrityError as e: 
        print(e)
# Not full fucntional yet. Need to filter out the shows to make sure that there are not duplicates. 
def show_list(): 

    url = 'https://app.ticketmaster.com/discovery/v2/events.json?classificationName=music&stateCode=MN&apikey=7CyQJ1JxlnqGBJe0uEkZw9h8SMvjoLQ9'
    
    try:
        data = requests.get(url).json()
        events = data['_embedded']['events']

        for event in events:

                venue_name =event['venues'][0]['name']
                print(artist_name)

                
    except Exception as e: 
            print('Error fetching shows')
            print(e)


show_list()