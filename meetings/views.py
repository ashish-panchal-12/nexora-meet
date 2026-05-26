from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Meeting
from .forms import MeetingForm, JoinMeetingForm


@login_required
def dashboard(request):
    hosted   = Meeting.objects.filter(host=request.user)
    joined   = request.user.joined_meetings.exclude(host=request.user)
    join_form = JoinMeetingForm()
    return render(request, 'meetings/dashboard.html', {
        'hosted':    hosted,
        'joined':    joined,
        'join_form': join_form,
    })


@login_required
def create_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting      = form.save(commit=False)
            meeting.host = request.user
            meeting.save()
            messages.success(request, f'Meeting "{meeting.title}" created!')
            return redirect('room', meeting_id=meeting.meeting_id)
    else:
        form = MeetingForm()
    return render(request, 'meetings/create_meeting.html', {'form': form})


@login_required
def join_meeting(request):
    if request.method == 'POST':
        form = JoinMeetingForm(request.POST)
        if form.is_valid():
            meeting_id = form.cleaned_data['meeting_id'].strip().upper()
            try:
                meeting = Meeting.objects.get(meeting_id=meeting_id, is_active=True)
                meeting.participants.add(request.user)
                return redirect('room', meeting_id=meeting.meeting_id)
            except Meeting.DoesNotExist:
                messages.error(request, 'Meeting not found or is no longer active.')
    else:
        form = JoinMeetingForm()
    return render(request, 'meetings/join_meeting.html', {'form': form})


@login_required
def room(request, meeting_id):
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id)
    if request.user != meeting.host:
        meeting.participants.add(request.user)
    return render(request, 'meetings/room.html', {
        'meeting':  meeting,
        'username': request.user.get_full_name() or request.user.username,
    })


@login_required
def end_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id, host=request.user)
    meeting.is_active = False
    meeting.save()
    messages.info(request, f'Meeting "{meeting.title}" has ended.')
    return redirect('dashboard')


@login_required
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id, host=request.user)
    meeting.delete()
    messages.success(request, 'Meeting deleted.')
    return redirect('dashboard')


@login_required
def meeting_api(request, meeting_id):
    """REST endpoint to get meeting details."""
    meeting = get_object_or_404(Meeting, meeting_id=meeting_id)
    return JsonResponse({
        'id':          meeting.meeting_id,
        'title':       meeting.title,
        'host':        meeting.host.username,
        'is_active':   meeting.is_active,
        'created_at':  meeting.created_at.isoformat(),
        'participants': meeting.participant_count(),
    })