import uuid
import os
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import  Group, User
from PIL import Image
from django.utils.text import slugify
from django.shortcuts import reverse


User = get_user_model()

#function to rename avatar file on upload
def path_and_rename(instance, filename):
    upload_to = 'groups_pics'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(instance.name, instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}-{}.{}'.format(uuid.uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

# Create your models here.
class CustomGroup(Group):
    TYPES = (
        ("one_book", "One Book"),
        ("several_books", "Several Books"),
        ("library", "Library"),
        ("wishlist", "Wish List"),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable = False, primary_key=True, unique=True)
    kname = models.CharField(max_length=50, unique=False, null=False, blank=False)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    group_pic = models.ImageField(upload_to=path_and_rename, null=True, blank = True)
    members = models.ManyToManyField(User, related_name="group_members")
    description = models.TextField(blank=True, null=True, max_length=500)
    group_type = models.CharField(max_length=20, choices=TYPES, default="one_book")
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def get_absolute_url(self):
        return reverse('group-detail', args=[self.uuid])
    
    def save(self, *args, **kwargs):
        super().save()
        # create slug
        if not self.name:
            self.name = self.kname + '_' + str(self.id) 
        if not self.slug:
            self.slug = slugify(self.kname + '_' + str(self.uuid))
        super(CustomGroup, self).save(*args, **kwargs)

    def __str__(self):
        return self.name