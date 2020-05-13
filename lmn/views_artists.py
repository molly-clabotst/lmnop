from django.shortcuts import render, redirect, get_object_or_404

from .models import Venue, Artist, Note, Show
from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def venues_for_artist(request, artist_pk):   # pk = artist_pk

    """ Get all of the venues where this artist has played a show """

    shows = Show.objects.filter(artist=artist_pk).order_by('-show_date')  # most recent first
    artist = Artist.objects.get(pk=artist_pk)

    return render(request, 'lmn/venues/venue_list_for_artist.html', { 'artist' : artist, 'shows' :shows })

''' 
    imported module :Paginator, EmptyPage, PageNotAnInteger 
    empty space is displayed if there are no list in the database
    paginator method is supplied with 2 argument. the list object and the maximum
    number of page to display on each page
'''
def artist_list(request):
    form = ArtistSearchForm()
    search_name = request.GET.get('search_name')
    if search_name:
        artist_list = Artist.objects.filter(name__icontains=search_name).order_by('name')
        page = request.GET.get('page', 1)
    else:
        artist_list= Artist.objects.all().order_by('name')
        #pagination process
        page = request.GET.get('page', 1)

    paginator = Paginator(artist_list, 10) # display max of 10 list
    try:
        artists = paginator.page(page)
    except PageNotAnInteger:
        artists = paginator.page(1)
    except EmptyPage:
        artists = paginator.page(paginator.num_pages)

    return render(request, 'lmn/artists/artist_list.html', { 'artists': artists, 'form': form, 'search_term': search_name })


def artist_detail(request, artist_pk):
    artist = get_object_or_404(Artist, pk=artist_pk)
    return render(request, 'lmn/artists/artist_detail.html' , { 'artist': artist })
