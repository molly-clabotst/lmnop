from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import re, datetime
from datetime import timezone




class TestAddNoteUnauthentictedUser(TestCase):

    fixtures = [ 'testing_artists', 'testing_venues', 'testing_shows' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_add_note_unauthenticated_user_redirects_to_login(self):
        response = self.client.get( '/notes/add/1/', follow=True)  # Use reverse() if you can, but not required.
        # Should redirect to login; which will then redirect to the notes/add/1 page on success.
        self.assertRedirects(response, '/accounts/login/?next=/notes/add/1/')


class TestAddNotesWhenUserLoggedIn(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_save_note_for_non_existent_show_is_error(self):
        new_note_url = reverse('lmn:new_note', kwargs={'show_pk':100})
        response = self.client.post(new_note_url)
        self.assertEqual(response.status_code, 404)


    def test_can_save_new_note_for_show_blank_data_is_error(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('lmn:new_note', kwargs={'show_pk':1})

        # No post params
        response = self.client.post(new_note_url, follow=True)
        # No note saved, should show same page
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no title
        response = self.client.post(new_note_url, {'text':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no text
        response = self.client.post(new_note_url, {'title':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # nothing added to database
        self.assertEqual(Note.objects.count(), initial_note_count)   # 2 test notes provided in fixture, should still be 2


    def test_add_note_database_updated_correctly(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('lmn:new_note', kwargs={'show_pk':1})

        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)

        # Verify note is in database
        new_note_query = Note.objects.filter(text='ok', title='blah blah')
        self.assertEqual(new_note_query.count(), 1)

        # And one more note in DB than before
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

        # Date correct?
        now = datetime.datetime.today()
        posted_date = new_note_query.first().posted_date
        self.assertEqual(now.date(), posted_date.date())  # TODO check time too


    def test_redirect_to_note_detail_after_save(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('lmn:new_note', kwargs={'show_pk':1})
        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)
        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        self.assertRedirects(response, reverse('lmn:note_detail', kwargs={'note_pk': new_note.pk }))


class TestUserProfile(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    # verify correct list of reviews for a user
    def test_user_profile_show_list_of_their_notes(self):
        # get user profile for user 2. Should have 2 reviews for show 1 and 2.
        response = self.client.get(reverse('lmn:user_profile', kwargs={'user_pk':2}))
        notes_expected = list(Note.objects.filter(user=2).order_by('-posted_date'))
        notes_provided = list(response.context['notes'])
        self.assertTemplateUsed('lmn/users/user_profile.html')
        self.assertEqual(notes_expected, notes_provided)

        # test notes are in date order, most recent first.
        # Note PK 3 should be first, then PK 2
        first_note = response.context['notes'][0]
        self.assertEqual(first_note.pk, 3)

        second_note = response.context['notes'][1]
        self.assertEqual(second_note.pk, 2)


    def test_user_with_no_notes(self):
        response = self.client.get(reverse('lmn:user_profile', kwargs={'user_pk':3}))
        self.assertFalse(response.context['notes'])

class TestUserAuthentication(TestCase):

    ''' Some aspects of registration (e.g. missing data, duplicate username) covered in test_forms '''
    ''' Currently using much of Django's built-in login and registration system'''

    def test_user_registration_logs_user_in(self):
        response = self.client.post(reverse('lmn:register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az', 'password2':'feRpj4w4pso3az', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)

        # Assert user is logged in - one way to do it...
        user = auth.get_user(self.client)
        self.assertEqual(user.username, 'sam12345')

        # This works too. Don't need both tests, added this one for reference.
        # sam12345 = User.objects.filter(username='sam12345').first()
        # auth_user_id = int(self.client.session['_auth_user_id'])
        # self.assertEqual(auth_user_id, sam12345.pk)


    def test_user_registration_redirects_to_correct_page(self):
        # TODO If user is browsing site, then registers, once they have registered, they should
        # be redirected to the last page they were at, not the homepage.
        response = self.client.post(reverse('lmn:register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az@1!2', 'password2':'feRpj4w4pso3az', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)

        self.assertRedirects(response, reverse('lmn:homepage'))   # FIXME Fix code to redirect to last page user was on before registration.
        self.assertContains(response, 'sam12345')  # Homepage has user's name on it
