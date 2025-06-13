Je veux que deux users puissent se connecter comme amis en utilisant un code profil

#models.py

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
    friends = models.ManyToManyField("self", blank=True)
    profile_code = models.CharField(max_length=50, null=False, blank=False, unique=True)
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

        # create profile code
        if not self.profile_code:
            pseudo_4 = self.pseudo[0:3]
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            self.profile_code = pseudo_4 + random_string
        # create slug
        if not self.slug:
            self.slug = slugify(self.pseudo + '_' + str(self.id))

        super(CustomUser, self).save(*args, **kwargs)

#forms.py

class InviteFriendForm(forms.ModelForm):
    profile_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_("Friend's Code")}), required=True)

#views.py
def connect_with_friend(request):
    user = request.user

    if request.method == 'POST':
        form = InviteFriendForm(request.POST)
        if form.is_valid():
            code = form.profile_code
            print(code)
            if User.objects.get(profile_code == code).exists:
                friend = User.objects.filter(profile_code == code)
                print(friend)
                if friend in user.friends:
                    pass
                else:
                    user.friends.append(friend)
                    user.save()
            else:
                print("il n'existe pas")
        
        else:
            for error in list(form.errors.values()):
                print(request, error)

    else:
        print("problème")
        form = InviteFriendForm(request.POST)

    return render(request, 'users/connect_with_friend.html', {'form':form, 'user':user})