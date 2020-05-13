from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import re, datetime
from datetime import timezone

class TestEmptyViews(TestCase):

    ''' main views - the ones in the navigation menu'''

    def test_with_no_notes_returns_empty_list(self):
        response = self.client.get(reverse('lmn:latest_notes'))
        self.assertFalse(response.context['notes'])  # An empty list is false


class TestNotes(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_latest_notes(self):
        response = self.client.get(reverse('lmn:latest_notes'))
        expected_notes = list(Note.objects.all())
        # Should be note 3, then 2, then 1
        context = response.context['notes']
        first, second, third = context[0], context[1], context[2]
        self.assertEqual(first.pk, 3)
        self.assertEqual(second.pk, 2)
        self.assertEqual(third.pk, 1)


    def test_notes_for_show_view(self):
        # Verify correct list of notes shown for a Show, most recent first
        # Show 1 has 2 notes with PK = 2 (most recent) and PK = 1
        response = self.client.get(reverse('lmn:notes_for_show', kwargs={'show_pk':1}))
        context = response.context['notes']
        first, second = context[0], context[1]
        self.assertEqual(first.pk, 2)
        self.assertEqual(second.pk, 1)


    def test_correct_templates_uses_for_notes(self):
        response = self.client.get(reverse('lmn:latest_notes'))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        response = self.client.get(reverse('lmn:note_detail', kwargs={'note_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_detail.html')

        response = self.client.get(reverse('lmn:notes_for_show', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        # Log someone in
        self.client.force_login(User.objects.first())
        response = self.client.get(reverse('lmn:new_note', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/new_note.html')
