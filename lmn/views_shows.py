from django.shortcuts import render, redirect, get_object_or_404

from .models import Note, Show

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

""" view shows that have the most notes"""
def show_with_most_notes(request):
    shows = Show.objects.all().order_by('-show_date' )
    print (shows)
    messages.info(request, f'the most note:{shows}')
    #return render(request, 'lmn/notes/most_note_for_show.html')
    return render(request, 'lmn/notes/most_note_for_show.html', {'shows': shows})
