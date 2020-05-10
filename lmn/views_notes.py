from django.shortcuts import render, redirect, get_object_or_404

from .models import Venue, Artist, Note, Show
from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, UserSearchOwnNotesForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden



@login_required
def new_note(request, show_pk):

    show = get_object_or_404(Show, pk=show_pk)

    if request.method == 'POST' :

        form = NewNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.show = show
            note.save()
            return redirect('lmn:note_detail', note_pk=note.pk)

    else :
        form = NewNoteForm()

    return render(request, 'lmn/notes/new_note.html' , { 'form': form , 'show': show })


def latest_notes(request):
    notes = Note.objects.all().order_by('-posted_date')
    return render(request, 'lmn/notes/note_list.html', { 'notes': notes })


def notes_for_show(request, show_pk):   # pk = show pk

    # Notes for show, most recent first
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')
    show = Show.objects.get(pk=show_pk)  
    return render(request, 'lmn/notes/note_list.html', { 'show': show, 'notes': notes } )



def note_detail(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html' , { 'note': note })

"""user can search fro their own note by specific title"""
def user_view_own_notes(request, user_pk):
    #TODO if user has made a search, what di they search for ?
    #usernotes = Note.objects.filter(user=user_pk).filter(by title).order_by('-posted_date')

    user_search_title = UserSearchOwnNotesForm()
    user = User.objects.get(pk=user_pk,)
    #usernotes = Note.objects.filter(user=user.pk).order_by('-posted_date')
    usernotes = Note.objects.filter(user=user_pk).filter(title='?').order_by('-title')
    return render(request, 'lmn/notes/user_view_own_notes.html', { 'user': user , 'notes': usernotes, 'search_form': user_search_title }) 
       