from django.shortcuts import render, redirect, get_object_or_404

from .models import Venue, Artist, Note, Show

from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, NoteEditPhotoForm, UserSearchOwnNotesForm




from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from django.http import HttpResponseForbidden

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




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


''' 
    imported module :Paginator, EmptyPage, PageNotAnInteger 
    empty space is displayed if there are no list in the database
    paginator method is supplied with 2 argument. the list object and the maximum
    number of page to display on each page
'''
def latest_notes(request):
    note_list = Note.objects.all().order_by('-posted_date')
    page = request.GET.get('page', 1)

    paginator = Paginator(note_list, 10) #display maximum of 10 list of Notes per page
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    return render(request, 'lmn/notes/note_list.html', { 'notes': notes })



def notes_for_show(request, show_pk):  # pk = show pk

    notes = Note.objects.filter(show=show_pk).order_by('posted_date')
    show = Show.objects.get(pk=show_pk)
    return render(request, 'lmn/notes/note_list.html', {'show': show, 'notes': notes})



def note_detail(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)

    if request.method == 'POST':
        photo_form = NoteEditPhotoForm(request.POST, request.FILES, instance=note)

        if photo_form.is_valid():
            photo_form.save()

        return redirect('lmn:note_detail', note_pk=note_pk)
    else:
        photo_form = NoteEditPhotoForm(instance=note)
    return render(request, 'lmn/notes/note_detail.html', {'note': note, 'photo_form': photo_form})



def delete_note(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)

    if request.method == 'POST':
        note.delete()
        return redirect('lmn:latest_notes')
    context = {
        'note': note,
    }
    return render(request, 'lmn/notes/delete_note.html', context)



"""user can search fro their own note by specific title"""
def user_view_own_notes(request, user_pk):
    #TODO if user has made a search, what di they search for ?
    user_search_title_form = UserSearchOwnNotesForm()
    search_title = ''
    user = User.objects.get(pk=user_pk,)
    if user_search_title_form.is_valid():
        search_title = user_search_title_form.cleaned_data['usernotes']
        notes = Note.objects.filter(title__icontains=search_title)
    else:
        notes = Note.objects.all()   
    return render(request, 'lmn/notes/user_view_own_notes.html', { 'user': user , 'notes': notes, 'search_form': user_search_title_form }) 
       

