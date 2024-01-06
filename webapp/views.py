from django.shortcuts import render, redirect

from rumi.settings import LOGIN_REDIRECT_URL
from .forms import RegistrationForm,PetForm,RoommatePreferencesForm,UserProfileForm,InterestForm,RoommateSearchForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import UserProfile,Pet,RoommatePreferences,Interest,UserInterest,ChatRoom,Chat,UserActivation
from datetime import date
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import HttpResponseBadRequest
from datetime import date
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError

import threading


# Create your views here.


def home(request):
    return render(request, 'webapp/index.html')

def about(request):
    return render(request, 'webapp/index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            user = form.save()
            user.is_active = False
            user.save()
            # messages.success(request, 'Your account has been created! You can now log in.')
            # return redirect('login')  # Redirect to login page

            # Create email_token for the user
            email_token = str(uuid.uuid4())
            UserActivation.objects.create(user=user, email_token=email_token)

            # Send verification email
            verification_link = request.build_absolute_uri(reverse('email_verify', args=[email_token]))

            # send_mail(
            #     'Verify your email',
            #     f'Please click on the link to verify your email: {verification_link}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )

            # Create and start the email thread
            email_thread = threading.Thread(target=send_mail, args=(
                'Verify your email',
                f'Please click on the link to verify your email: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                False
                )
            )

            email_thread.start()

            return render(request, 'registration/verify_email_done.html')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def email_verify(request, email_token):
    try:
        user_profile = UserActivation.objects.get(email_token=email_token)
        user_profile.user.is_active = True
        user_profile.user.save()
        user_profile.save()
        messages.success(request, 'Email verified successfully. You can now login.')
    except UserActivation.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('login')

@login_required
def profile(request):
    try:
        current_user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        current_user_profile = None
    
    try:
        current_pet = Pet.objects.get(user=request.user)
    except Pet.DoesNotExist:
        current_pet = None

    try:
        current_interest = Interest.objects.get(user=request.user)
    except Interest.DoesNotExist:
        current_interest = None

    try:
        current_room_pref = RoommatePreferences.objects.get(user=request.user)
    except RoommatePreferences.DoesNotExist:
        current_room_pref = None

    if request.method == 'POST':
        userform = UserProfileForm(request.POST, request.FILES, instance=current_user_profile)
        petform = PetForm(request.POST, instance=current_pet)
        preferenceform = RoommatePreferencesForm(request.POST, instance=current_room_pref)
        interestform = InterestForm(request.POST, instance=current_interest)

        with transaction.atomic():
            if userform.is_valid() and petform.is_valid() and preferenceform.is_valid() and interestform.is_valid():
                user_profile = userform.save(commit=False)
                user_profile.user = request.user
                user_profile.save()
                
                
                pet_instance = petform.save(commit=False)
                pet_instance.user = request.user
                pet_instance.save()
                petform.save_m2m() 

                interest_instance = interestform.save(commit=False)
                interest_instance.user = request.user
                interest_instance.save()
                interestform.save_m2m() 

                room_preference_instance = preferenceform.save(commit=False)
                room_preference_instance.user = request.user
                room_preference_instance.save()

                messages.success(request, 'Your profile was successfully updated!')
                return redirect('search_roommates')

            else:
                messages.error(request, 'There was an error updating your profile. Please check the provided data.')
                for field, errors in {**userform.errors, **petform.errors, **preferenceform.errors, **interestform.errors}.items():
                    for error in errors:
                        messages.error(request, f"{field} - {error}")

    else:
        petform = PetForm(instance=current_pet)
        preferenceform = RoommatePreferencesForm(instance=current_room_pref)
        userform = UserProfileForm(instance=current_user_profile)
        interestform = InterestForm(instance=current_interest)

    return render(request, 'webapp/profile.html', {'userform': userform, 'petform': petform, 'preferenceform': preferenceform, 'interestform':interestform, 'image_url' : current_user_profile.profile_picture.url if current_user_profile and current_user_profile.profile_picture else None })


@login_required
def dashboard(request):

    if not UserProfile.objects.filter(user=request.user).exists():
        messages.warning(request,"You need to update your profile first.")
        return redirect('profile')


    # Retrieve UserInterest objects related to the current user
    interests = UserInterest.objects.filter(Q(interested_in=request.user)|Q(user=request.user))

    unconfirmed_roommates = []
    confirmed_roommates = []

    for interest in interests:
        if interest.user == request.user:
            try:
                user_profile = UserProfile.objects.get(user=interest.interested_in)
            except UserProfile.DoesNotExist:
                break
        else:
            try:
                user_profile = UserProfile.objects.get(user=interest.user)
            except UserProfile.DoesNotExist:
                break
        bio = user_profile.about if user_profile.about else "No biography available"
        dob = user_profile.dob
        gender = user_profile.sex if user_profile.sex else "Not specified"
        
        roommate_data = {
            'id': user_profile.user.id,
            'name': user_profile.user.username,  # Assuming username is enough; adapt as needed
            'image_url': user_profile.profile_picture.url if user_profile.profile_picture else None,
            'bio': bio,
            'age': user_profile.get_age(),
            'gender': gender,
            'interest':interest.id
        }

        if interest.accept:  # Confirmed
            confirmed_roommates.append(roommate_data)
        elif not interest.accept and not interest.reject and not interest.user == request.user:  # Pending
            unconfirmed_roommates.append(roommate_data)

    return render(request, 'webapp/dashboard.html', {'unconfirmed_roommates': unconfirmed_roommates, 'confirmed_roommates': confirmed_roommates})


@login_required
def user_detail(request, user_id):
    # Fetch user details using the provided user_id
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    roommate_preferences = get_object_or_404(RoommatePreferences, user__id=user_id)
    self_roommate_preferences = get_object_or_404(RoommatePreferences, user__id=request.user.pk)
    interests = get_object_or_404(Interest, user__id=user_id)
    user_pets = get_object_or_404(Pet, user__id=user_id)

    # Single query to check both directions of interest
    user_interest = UserInterest.objects.filter(
        Q(user=request.user, interested_in=user_id) |
        Q(user=user_id, interested_in=request.user.id)
    ).first()

    if user_interest:
        if user_interest.user == request.user:
            direction = 'outgoing'
        else:
            direction = 'incoming'

        if user_interest.accept:
            status = 'accepted'
        elif user_interest.reject:
            status = 'rejected'
        else:
            status = 'pending'
        user_interest_id = user_interest.id
    else:
        status = 'none'
        user_interest_id = None
        direction = 'none'

    comp_analysis = self_roommate_preferences.compare(roommate_preferences)

    context = {
        'user_profile': user_profile,
        'roommate_preferences': roommate_preferences,
        'user_interests': interests,
        'user_pets': user_pets,
        'status': status,
        'user_interest_id': user_interest_id,
        'direction': direction,
        'self_data' : comp_analysis[0],
        'other_data' : comp_analysis[1],
        'cols' : comp_analysis[2]
    }

    return render(request, 'webapp/roommatedetails.html', context)

@login_required
def accept_view(request, interest_id):
    try:
        interest = get_object_or_404(UserInterest, id=interest_id)
        interest.accept_interest()
        messages.success(request, "Roommate request accepted successfully.")
    except ValidationError as e:
        # If there are multiple error messages, iterate through them
        if hasattr(e, 'error_dict'):
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, error)
        else:
            # If it's a single error message
            messages.error(request, e.messages[0])
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Redirect to the previous page or to the homepage
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def reject_view(request, interest_id):
    interest = get_object_or_404(UserInterest, id=interest_id)
    interest.reject_interest()
    
    # Get the previous page URL, if it exists, otherwise default to homepage
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def search_roommates(request):
    if not UserProfile.objects.filter(user=request.user).exists():
        messages.warning(request,"You need to update your profile first.")
        return redirect('profile')

    if request.method == "POST":
        form = RoommateSearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data.get("keyword")
            city = form.cleaned_data.get("city")
            gender = form.cleaned_data.get("gender")
            age_min = form.cleaned_data.get("age_min")
            age_max = form.cleaned_data.get("age_max")

            # Exclude users who have already been accepted or rejected by the logged-in user
            excluded_users = UserInterest.objects.filter(Q(user=request.user) | Q(interested_in=request.user)).values_list('user', 'interested_in')
            excluded_user_ids = set([item for sublist in excluded_users for item in sublist])

            # Filter the UserProfile based on the criteria
            profiles = UserProfile.objects.exclude(user__in=excluded_user_ids).exclude(user=request.user)

            if keyword:
                profiles = profiles.filter(
                    Q(user__username__icontains=keyword) |
                    Q(user__first_name__icontains=keyword) |
                    Q(user__last_name__icontains=keyword)
                )
            if city:
                profiles = profiles.filter(city=city)
            if gender:
                profiles = profiles.filter(sex=gender)
            if age_min:
                min_date = date.today().replace(year=date.today().year - age_min)
                profiles = profiles.filter(dob__lte=min_date)
            if age_max:
                max_date = date.today().replace(year=date.today().year - age_max)
                profiles = profiles.filter(dob__gte=max_date)

        else:
            profiles = UserProfile.objects.none()
    else:
        form = RoommateSearchForm()
        excluded_users = UserInterest.objects.filter(Q(user=request.user) | Q(interested_in=request.user)).values_list('user', 'interested_in')
        excluded_user_ids = set([item for sublist in excluded_users for item in sublist])
        profiles = UserProfile.objects.exclude(user__in=excluded_user_ids).exclude(user=request.user)

    # Pagination
    profiles = profiles.order_by('-created_at')  # Order the queryset
    paginator = Paginator(profiles, 10) # Show 10 profiles per page
    page = request.GET.get('page')
    try:
        paginated_profiles = paginator.page(page)
    except PageNotAnInteger:
        paginated_profiles = paginator.page(1)
    except EmptyPage:
        paginated_profiles = paginator.page(paginator.num_pages)

    return render(request, 'webapp/searchroommates.html', {'form': form, 'profiles': paginated_profiles})



@login_required
def request_connection(request, user_id):
    # Get the target user
    target_user = get_object_or_404(User, pk=user_id)

    # Check if a connection request already exists
    connection_exists = UserInterest.objects.filter(user=request.user, interested_in=target_user).exists()

    if connection_exists:
        messages.warning(request, 'Connection request already sent to this user.')
    else:
        # Create a new connection request
        UserInterest.objects.create(user=request.user, interested_in=target_user)
        messages.success(request, f'Connection request sent to {target_user.username}.')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def chat_list(request):
    # Get chat rooms where the current user is either user1 or user2
    chat_rooms = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    
    # Prepare a list to hold chat rooms, their respective other user's name, and the last chat message
    chats_with_users = []

    for room in chat_rooms:
        other_user = room.user1 if room.user2 == request.user else room.user2
        last_chat = Chat.objects.filter(room=room).order_by('-timestamp').first()
        last_message = last_chat.content if last_chat else "No messages yet"
        last_message_time = last_chat.timestamp if last_chat else None
        userprofile = UserProfile.objects.get(user=other_user)
        chats_with_users.append({
            'image_url':  userprofile.profile_picture.url if userprofile.profile_picture else None,
            'room_name': room.name,
            'other_user': other_user,  # or other_user.get_full_name() if you want full name
            'last_message': last_message,
            'last_message_time': last_message_time
        })
    from datetime import datetime, timedelta
    import pytz

    def sort_key(x):
        if x['last_message_time'] is None:
            return datetime.now(pytz.utc) - timedelta(days=36500)  # Making it timezone-aware with UTC timezone
        # Ensure the datetime is timezone-aware
        return x['last_message_time'].astimezone(pytz.utc)

    chats_with_users = sorted(chats_with_users, key=sort_key, reverse=True)

    # chats_with_users = sorted(chats_with_users, key=lambda x: x['last_message_time'], reverse=True)
    return render(request, "webapp/chat_list.html", {
        'chats_with_users': chats_with_users
    })

@login_required
def chat(request, room_name):
    try:
        # Extracting user IDs from the room_name
        try:
            user1_id, user2_id = map(int, room_name.split('_'))
        except ValueError:
            # Handle the case where room_name format is incorrect
            return HttpResponseBadRequest("Invalid room name format")

        # user_instance_1 = get_object_or_404(User, pk=user1_id)
        # user_instance_2 = get_object_or_404(User, pk=user2_id)

        room = ChatRoom.objects.filter(name=room_name).first()
        chats = []

        if room:
            chats = Chat.objects.filter(room=room)
        else:
            room = ChatRoom(name=room_name)  # Name provided, user1 and user2 will be derived in the save method
            room.save()

        other_user = room.user1 if room.user2 == request.user else room.user2
    except Exception as e:
        messages.error(request,str(e))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, "webapp/chat_room.html", {"room_name": room_name, 'chats': chats, 'other_user':other_user})

