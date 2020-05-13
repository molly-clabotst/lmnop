from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import datetime

# Every model gets a primary key field by default.

# Users, venues, shows, artists, notes

# User is provided by Django. The email field is not unique by
# default, so add this to prevent more than one user with the same email.
User._meta.get_field('email')._unique = True

# Require email, first name and last name
User._meta.get_field('email')._blank = False
User._meta.get_field('last_name')._blank = False
User._meta.get_field('first_name')._blank = False


'''User profile information'''


class UserProfile(models.Model):
    user = models.ForeignKey('auth.User', blank=False, on_delete=models.CASCADE)
    favArtist = models.CharField(max_length=200, blank=True)
    favShow = models.CharField(max_length=200, blank=True)
    favVenue = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.favArtist}, {self.favShow}, {self.favVenue}'


''' A music artist '''


class Artist(models.Model):
    name = models.CharField(max_length=200, blank=False);

    def __str__(self):
        return "Artist: " + self.name


''' A venue, that hosts shows. '''


class Venue(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=True)
    city = models.CharField(max_length=200, blank=False)
    state = models.CharField(max_length=20, blank=False)  # What about international?

    def __str__(self):
        return 'Venue name: {} in {}, {}'.format(self.name, self.city, self.state)


''' A show - one artist playing at one venue at a particular date. '''


class Show(models.Model):
    show_date = models.DateTimeField(blank=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return 'Show with artist {} at {} on {}'.format(self.artist, self.venue, self.show_date)


''' One user's opinion of one show. '''


class Note(models.Model):
    RATINGS = (
        ('Poor', 'Poor Show'),
        ('Average', 'Average Show'),
        ('Good', 'Good Show'),
        ('Very Good', 'Very Good Show'),
        ('Excellent', 'Excellent Show'))

    show = models.ForeignKey(Show, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    text = models.TextField(max_length=1000, blank=False)
    posted_date = models.DateTimeField(blank=False, auto_now=True)
    rating = models.CharField(choices=RATINGS, default='Good', max_length=15)
    photo = models.ImageField(upload_to='user_images/', blank=True, null=True)

    def save(self, *args, **kwargs):

        old_note = Note.objects.filter(pk=self.pk).first()
        if old_note and old_note.photo:
            if old_note.photo != self.photo:
                self.delete_photo(old_note.photo)
        super().save(*args, **kwargs)

    def delete_photo(self, photo):
        if default_storage.exists(photo.name):
            default_storage.delete(photo.name)

    def publish(self):
        posted_date = datetime.datetime.today()
        self.save()

    def __str__(self):
        photo_str = self.photo.url if self.photo else 'No Photo Uploaded!'
        return 'Note for user ID {} for show ID {} with title {} text {} posted on {}'.format(self.user, self.show,self.title, self.text,self.posted_date)

