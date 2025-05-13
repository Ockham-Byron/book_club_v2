from uuid import uuid4
import os
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from PIL import Image
from django.db import models

#function to rename avatar file on upload
def path_and_rename(instance, filename):
    upload_to = 'users_pictures'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(instance.username, instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}-{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)



class CustomUser(AbstractUser):
    AVATAR = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
    )
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    email = models.EmailField(unique=True)
    is_mail_visible = models.BooleanField(default=False)
    is_name_visible = models.BooleanField(default=False)
    pseudo = models.CharField(max_length=255, null=False, blank="False", default="Anonymous")
    avatar_color = models.CharField(max_length=255, default="#ec6a52", null=True)
    bio = models.CharField(max_length=500, null=True, blank="True")
    profile_pic = models.ImageField(blank=True, null=True, upload_to=path_and_rename)
    is_rgpd = models.BooleanField(default=False)
    email_is_verified = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pseudo

    
    def save(self, *args, **kwargs):
        super().save()
        # resizing images
        if self.profile_pic:
            img = Image.open(self.profile_pic.path)

            if img.height > 100 or img.width > 100:
                new_img = (100, 100)
                img.thumbnail(new_img)
                img.save(self.profile_pic.path)
        else:
            pass
        # create slug
        if not self.slug:
            self.slug = slugify(self.pseudo + '_' + str(self.id))
        super(CustomUser, self).save(*args, **kwargs)
    
