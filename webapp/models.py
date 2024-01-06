from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    CITY_CHOICES = [
        ('', '-----'),
        ('Atlanta', 'Atlanta'),
        ('Columbus', 'Columbus'),
        ('Augusta', 'Augusta'),
        ('Macon', 'Macon'),
        ('Savannah', 'Savannah'), 
    ]
    SEX_CHOICES = [('', '-----'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    EDUCATION_CHOICES = [
        ('', '-----'),
        ('shs', 'Some High School'),
        ('hs', 'High School'),
        ('col', 'College'),
        ('grad', 'Graduate'),
        ('others', 'Others'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/',null=True, blank=True)
    dob = models.DateField()
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    occupation = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    education = models.CharField(max_length=10, choices=EDUCATION_CHOICES)
    move_in_date = models.DateField()
    about = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)    

    def get_age(self):
        today = date.today()
        born = self.dob
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class RoommatePreferences(models.Model):
    THREE_OPTION_CHOICES = [('', '-----'), ('Yes', 'Yes'), ('Sometimes', 'Sometimes'), ('No', 'No')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sleep_hours = models.PositiveIntegerField()  # assuming you won't have negative hours
    drinks = models.CharField(max_length=10, choices=THREE_OPTION_CHOICES)
    drugs = models.CharField(max_length=10, choices=THREE_OPTION_CHOICES)
    smoke = models.CharField(max_length=10, choices=THREE_OPTION_CHOICES)
    loud_music = models.CharField(max_length=10, choices=THREE_OPTION_CHOICES)
    rooms = models.PositiveIntegerField()
    budget = models.PositiveIntegerField()
    meals = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  

    def save(self, *args, **kwargs):
        # Check the number of accepted interests for the user
        accepted_count = UserInterest.objects.filter(user=self.user, accept=True).count()

        # If the updated number of roommates is less than the accepted interests, raise an error
        if self.rooms < accepted_count:
            raise ValidationError(f"Cannot set the number of roommates to {self.num_roommates}. You've already accepted {accepted_count} interests.")

        super(RoommatePreferences, self).save(*args, **kwargs)


    def compare(self, other):
        if self.user == other.user:
            raise ValidationError(f"Cannot Compare Self")

        def scale_to_hundred(values):
            total = sum(values)
            return [(value / total) * 100 for value in values]

        def scale_choices(value):
            lower_case_value = value.lower()
            if lower_case_value == 'sometimes':
                return 100
            return 50 if lower_case_value == 'yes' else 0

        # Assuming self_score and other_score are lists that contain either strings for choices
        # or lists of numbers for scale_to_hundred.
        self_scaled = []
        other_scaled = []
        self_score = [self.drinks,self.sleep_hours,self.drugs, self.smoke, self.loud_music,self.rooms,self.budget,self.meals]
        other_score = [other.drinks,other.sleep_hours,other.drugs, other.smoke, other.loud_music,other.rooms,other.budget,other.meals]
        cols = ['Drinks','Sleep Hours', 'Drugs', 'Smoke', 'Loud Music', 'Rooms', 'Budget', 'Meals']


        for self_value, other_value in zip(self_score, other_score):
            if isinstance(self_value, str):
                self_scaled.append(scale_choices(self_value))
                other_scaled.append(scale_choices(other_value))
            elif isinstance(int(self_value), int) and isinstance(int(other_value), int):
                val = scale_to_hundred([int(self_value),int(other_value)])
                self_scaled.append(val[0])
                other_scaled.append(val[1])

            else:
                raise ValueError("Unsupported data type in score lists.")

        return self_scaled, other_scaled, cols


class UserActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  
 
class InterestChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name

class PetChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interests = models.ManyToManyField(InterestChoice, blank=True)
    pets_allowed = models.ManyToManyField(PetChoice, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  

class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pets = models.ManyToManyField(PetChoice, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Sets the time when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  

class UserInterest(models.Model):
    user = models.ForeignKey(User, related_name='interests', on_delete=models.CASCADE)
    interested_in = models.ForeignKey(User, related_name='interested_by', on_delete=models.CASCADE)
    accept = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    class Meta:
        unique_together = ['user', 'interested_in']

    def __str__(self):
        return f"{self.user} interested in {self.interested_in}"

    def accept_interest(self):
        # Check the number of accepted interests for the user
        accepted_count = UserInterest.objects.filter(user=self.user, accept=True).count()

        # Fetch the user's profile
        user_preference = RoommatePreferences.objects.get(user=self.user)

        if accepted_count < user_preference.rooms:
            self.accept = True
            self.reject = False
            self.save()
        else:
            raise ValidationError("Error: Maximum number of roommates reached.")

    def reject_interest(self):
        self.accept = False
        self.reject = True
        self.save()


class Chat(models.Model):
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom', related_name="messages", on_delete=models.CASCADE)

from django.core.exceptions import ValidationError

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ensuring uniqueness
    user1 = models.ForeignKey(User, related_name="chatroom_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="chatroom_user2", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Split the name to derive user1 and user2
        user_ids = self.name.split('_')
        if len(user_ids) != 2:
            raise ValidationError("Invalid ChatRoom name format. Expected format: 'user1ID_user2ID'")
        if user_ids[0] == user_ids[1]:
                raise ValidationError("Invalid ChatRoom name format. Chat to self not allowed.")
        try:
            self.user1 = User.objects.get(pk=user_ids[0])
            self.user2 = User.objects.get(pk=user_ids[1])
        except User.DoesNotExist:
            raise ValidationError("One or both users specified in the ChatRoom name do not exist")

        # Sorting by ID to ensure the name format is always consistent
        sorted_user_ids = sorted(user_ids)
        self.name = f"{sorted_user_ids[0]}_{sorted_user_ids[1]}"
        
        super(ChatRoom, self).save(*args, **kwargs)




# INTEREST_CHOICES = [
#         ('Arts', 'Arts'),
#         ('Nature', 'Nature'),
#         ('Music', 'Music'),
#         ('Travel', 'Travel'),
#         ('Reading', 'Reading'),
#         ('Sports', 'Sports'),
#         ('Cooking', 'Cooking'),
#         ('Technology', 'Technology'),
#         ('Fitness', 'Fitness'),
#         ('Movies', 'Movies'),
#         ('Photography', 'Photography'),
#         ('Gaming', 'Gaming'),
#     ]  


# PET_CHOICES = [
#         ('Dog', 'Dog'),
#         ('Cat', 'Cat'),
#         ('Goat', 'Goat'),
#         ('Alpaca', 'Alpaca'),
#     ]
    