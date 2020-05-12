import requests
from django.http import HttpResponse
from django.db import IntegrityError
from django.db import models

import us 

from .models import Venue, Artist, Show

event_url ='https://app.ticketmaster.com/discovery/v2/events.json?classificationName=music'
venue_url = 'https://app.ticketmaster.com/discovery/v2/venues'
  
key = '7CyQJ1JxlnqGBJe0uEkZw9h8SMvjoLQ9'


def get_data(requests):
    try:
        venues = venue_response() # Broke the api calls into two fuctions. Figured this could reduce calls.
        events = event_response()

        get_artist(events)
        get_venue(venues)
        get_shows(events)
        return HttpResponse('ok')
        # gettign artist, venues and shows and providing an httpresponse if successful
    except Exception as e:
            print(e)
            return HttpResponse('failed')

def event_response():
    query = {'apikey' : key, 'stateCode' : 'MN' }
    try:
        data = requests.get(event_url, params=query).json() # api call for 'music' events with the statecode 'MN'
        events = data['_embedded']['events']
        return events
    except Exception as e:
        print(e)
def venue_response():    
    try:
        query = {'apikey': key , 'stateCode' : 'MN', 'name' : 'music'}
        data = requests.get(venue_url, params=query).json() # Retrives a JSON from ticketmaster
        venues = data['_embedded']['venues']
        return venues
    except Exception as e:
        print(e)

def get_artist(events):
    artist_names = [] # Empty list to hold all the artist output, using this to make sure check for duplicate entries.

    for event in events: # Cycles through the JSON and finds the event names, Better to use a for than a range, take note of that. 
        artist_name = (event['name'])
        artist_names += artist_name
        filtered_artist = Artist.objects.filter(name=artist_name)
        
        if artist_name not in artist_names: # Makes sure there are no duplicates.

            if (filtered_artist):    
                print('duplicate artist') # Maybe put something more meaningful here?      

            else:
                print(artist_name)
                new_artist =Artist(name=artist_name)
                new_artist.save()

def get_venue(venues):

    venues_names = [] # Create an empty list to store previously created venues.

    for venue in venues: # finds each venue in the json response
        venue_name = venue['name'] # assigning a variable to the venue_name
        venues_names += venue_name
        filtered_venue = Venue.objects.filter(name=venue_name) # Makes sure that only venues that are not already in the table.
        
        if(filtered_venue):
            print('Already added')
        else:
            venue_city = venue['city']['name'] # finding value for the venue city
            venue_state = venue['state']['name'] # assigning value for the venue state
            venue_state = stateAbbrevation(venue_state)
            venue_new = Venue(name=venue_name, city=venue_city, state=venue_state) # creates a .models/Venue object and assigns the values
            venue_new.save() # Saves the object into the database
            print(venue_name,venue_city,venue_state)

# Not full fucntional yet. Need to filter out the shows to make sure that there are not duplicates. 
def get_shows(events): 

    for event in events:
        artist_name = event['name']
        venue_name = event['_embedded']['venues'][0]['name']
        date = event['dates']['start']['dateTime']
        # grabbing the Artist object and the Venue object from the database. 
        filtered_artist = Artist.objects.filter(name=artist_name)
        filtered_venue = Venue.objects.filter(name=venue_name)

        if (filtered_artist) and (filtered_venue):
            artist = filtered_artist[0]
            venue = filtered_venue[0]
            event_new = Show(show_date=date, artist=artist, venue=venue)
            print(artist_name,venue_name, date)
        else:
            print('No shows.')

def stateAbbrevation(state):
# Had issues getting the Google cloud database to properly migrate changes to the model so this is my work around. 
# Converts the fullname to an its intials. 
    state_initals = us.states.lookup(state)
    return state_initals

if __name__ == "__main__":
    get_data(requests)