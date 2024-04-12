from uuid import uuid4
from django.db.models import Avg, Count
import os
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from groups.models import CustomGroup
from django.db import models
from datetime import datetime, timedelta, date

User = get_user_model()

#function to rename avatar file on upload
def path_and_rename(instance, filename):
    upload_to = 'covers'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(instance.username, instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}-{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

# Create your models here.
class Book(models.Model):
    
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    title = models.CharField(max_length=150, blank=False, null=False)
    author = models.CharField(max_length=150, blank=False, null=False)
    isbn = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pages = models.IntegerField(default = 0, blank=True, null=True)
    in_library = models.ManyToManyField(User, related_name="in_libraries", blank=True)
    in_wishlist = models.ManyToManyField(User, related_name="in_wishlist", blank=True)
    readers = models.ManyToManyField(User, related_name="readers", blank=True)
    readings = models.ManyToManyField(User, related_name="readings", blank=True)
    no_read = models.ManyToManyField(User, related_name="no_read", blank=True)
    wont_read = models.ManyToManyField(User, related_name="wont_read", blank=True)
    give_up = models.ManyToManyField(User, related_name="give_up", blank=True)
    cover=models.CharField(max_length=500, blank=True, null=True)
    picture=models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(CustomGroup, related_name="books", blank=True)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save()
        # create slug
        if not self.slug:
            self.slug = slugify(self.title + '_' + str(self.id))
        super(Book, self).save(*args, **kwargs)

    def averagereview(self):
        if Comment.objects.filter(book=self).exists():
            comments = Comment.objects.filter(book=self).aggregate(average=Avg('rating'))
            avg=0
            if ["average"] is not None:
                avg=float(comments["average"])
            return avg
        

    def countreview(self):
        comments = Comment.objects.filter(product=self).aggregate(count=Count('id'))
        cnt=0
        if comments["count"] is not None:
            cnt = int(comments["count"])
        return cnt



class CustomBook(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    book=models.ForeignKey(Book, related_name="book_origin", on_delete=models.PROTECT)
    admin = models.ForeignKey(User, related_name="admin", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True, null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    isbn = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    reservations = models.ManyToManyField(User, related_name="reservations", blank=True)
    cover=models.CharField(max_length=500, blank=True, null=True)
    picture=models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

    def __str__(self):
        return self.book.title
    
    def save(self, *args, **kwargs):
        super().save()
        if not self.title:
            self.title = self.book.title
        if not self.author:
            self.author = self.book.author
        if not self.isbn:
            self.isbn = self.book.isbn
        if not self.description:
            self.description = self.book.description
        if not self.pages:
            self.pages = self.book.pages
        if not self.cover:
            self.cover = self.book.cover
        if not self.picture:
            self.picture = self.book.picture

        # create slug
        if not self.slug:
            self.slug = slugify(self.title + '_' + self.admin + '_' + str(self.id))
        super(Book, self).save(*args, **kwargs)

class Comment(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    book=models.ForeignKey(Book, related_name="book_comments", on_delete=models.CASCADE)
    author=models.ForeignKey(User, related_name="user_comments", on_delete=models.CASCADE)
    rating=models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)], blank=False, null=False)
    message=models.CharField(max_length=500, blank=True, null=True)

class Meeting(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    book = models.ForeignKey(Book, related_name="meeting", on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, null=True, blank=True)
    meeting_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    attendees = models.ManyToManyField(User, related_name="attendees", blank=True)
    place = models.CharField(max_length=200, blank=True, null=True)

class Borrow(models.Model):
    PENDING = 'pending'
    NO_RESPONSE = 'no_response'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show' #the the delivery of the object did not take place
    ON_GOING = 'on_going'
    RETURNED = 'returned'
    LATE_RETURN = 'late_return' #the return of the object did not take place on time
    NO_RETURN = 'no_return' #object was not returned

    STATUS = [
        (PENDING, ('Waiting for confirmation')),
        (NO_RESPONSE, ("Owner didn't give a response")),
        (CONFIRMED, ('Confirmed')),
        (REJECTED, ('Cancelled by owner')),
        (CANCELLED, ('Cancelled by requester')),
        (NO_SHOW, ("Delivery  did not take place")),
        (ON_GOING, ('Product actually borrowed by requester ')),
        (RETURNED, ('Product returned by the borrower')),
        (LATE_RETURN, ("Return did not take place on time")),
        (NO_RETURN, ("Object not returned")),
    ]
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    custom_book = models.ForeignKey(CustomBook, on_delete=models.CASCADE, related_name="borrowing", unique=False, null=True)
    borrower = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="borrower", unique=False, null=True)
    demand_date = models.DateField(auto_now_add=True)
    
    borrow_start = models.DateField(auto_now_add=False, blank=False, null=False) 
    borrow_end = models.DateField(auto_now_add=False, blank=True, null=True)
    status = models.CharField(max_length=32, choices = STATUS, default=PENDING)
    late_return = models.BooleanField(default=False)

    def is_waiting_long(self):
        current_date = date.today()
        waiting_to_long_date = self.demand_date + timedelta(days=4)
        reservation_date_approching = self.reservation_start - timedelta(days=3)
        if current_date > waiting_to_long_date or current_date > reservation_date_approching:
            return True

    def __str__(self):
        return self.custom_book.book.title



    