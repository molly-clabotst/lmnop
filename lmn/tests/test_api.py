from django.contrib import auth

from lmn.models import Venue, Artist, Note, Show
from lmn import views_admin
from django.contrib.auth.models import User
from lmn import ticket_master_api
from mock import patch

import os
import requests
class TestAdminViews(TestCase):

    # Test API response
    @patch('lmn.ticket_master_api.get_data')
    def test_get_shows(self, mock_response):

        mock_artist = 'Beverly Cleary '
        mock_venue = 'Judy Blume'
        mock_city = 'Minneapolis'
        mock_state = 'Minnesota'
        mock_show_date = '2020-10-25T03:00:00Z'
        api_response = {'_embedded':{'events': [{0: {'name': mock_artist, 
                        '_embedded':{'venues': [{0: {'name': mock_venue, 'city': {'name': mock_city}, 'state': {'name': mock_state}}}]}},
                        'dates': {'start':{'dateTime': mock_show_date}}}]}}
        mock_response.side_effect = [api_response]

        artist = ticket_master_api.get_artist()
        venue = ticket_master_api.get_venue
        show = ticket_master_api.get_venue(artist, venue)
        
        self.assertEqual(mock_artist, artist.name)
        self.assertEqual(mock_venue, venue.name)
        self.assertEqual(mock_city, venue.city)
        self.assertEqual(mock_state, venue.state)
        self.assertEqual(mock_show_date, show.show_date)




    def test_response_200(self):
    # 200 respones means that it worked 
        classificaton = 'music'
        query = {'classificationName': classificaton, 'apikey': key}
        url = 'https://app.ticketmaster.com/discovery/v2/events.json?'
        request = requests.get(url, params=query)
        self.assertEqual(request.status_code, 200)




    def test_response_400(self):
        key = 'key'
        classificaton = 'willnotwork'
        query = {'classificationName': classificaton, 'apikey': key}
        url = 'https://app.ticketmaster.com/discovery/v2/events.json?'
        request = requests.get(url, params=query)
        self.assertEqual(request.status_code, 400)