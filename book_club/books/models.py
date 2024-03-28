from uuid import uuid4
from django.db.models import Avg, Count
import os
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from groups.models import CustomGroup
from django.db import models

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
    owner = models.ForeignKey(User, related_name='owner', blank=True, null=True, on_delete=models.CASCADE)
    reservations = models.ManyToManyField(User, related_name="reservations", blank=True)
    in_library = models.ManyToManyField(User, related_name="in_libraries", blank=True)
    in_wishlist = models.ManyToManyField(User, related_name="in_wishlist", blank=True)
    readers = models.ManyToManyField(User, related_name="readers", blank=True)
    cover=models.CharField(max_length=500, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(CustomGroup, related_name="books", blank=True)
    # slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     super().save()
    #     # create slug
    #     if not self.slug:
    #         self.slug = slugify(self.title + '_' + str(self.id))
    #     super(Book, self).save(*args, **kwargs)

    def averagereview(self):
        if Comment.objects.filter(dish=self).exists():
            comments = Comment.objects.filter(dish=self).aggregate(average=Avg('rating'))
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
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)


    