Comment récuperer les borrow correspondant à chaque user_kbook dont le status est "on_going" ?
# models.py

class Book(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    google_id = models.CharField(max_length=150, blank=True, null=True)
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
    genres = models.ManyToManyField(Genre, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(CustomGroup, related_name="books", blank=True)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

class CustomBook(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    book=models.ForeignKey(Book, related_name="kbook", on_delete=models.PROTECT)
    group = models.ForeignKey(CustomGroup, related_name="kbook_group", on_delete=models.CASCADE, blank=True, null=True)
    sharing_groups = models.ManyToManyField(CustomGroup, related_name="shared_book", blank=True)
    admin = models.ForeignKey(User, related_name="admin", on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE, blank=True, null=True)
    kowner = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    isbn = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    is_borrowable = models.BooleanField(blank=True, null=True, default=False)
    is_disponible = models.BooleanField(blank=True, null=True, default=False)
    cover=models.CharField(max_length=500, blank=True, null=True)
    picture=models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

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
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True)
    custom_borrower = models.CharField(max_length=150, null=True, blank=True)
    demand_date = models.DateField(auto_now_add=True)
    borrow_start = models.DateField(auto_now_add=True, blank=False, null=False) 
    borrow_end = models.DateField(auto_now_add=False, blank=True, null=True)
    status = models.CharField(max_length=32, choices = STATUS, default=PENDING)
    late_return = models.BooleanField(default=False)
    need_borrow_confirmation = models.BooleanField(default=False)
    need_return_confirmation = models.BooleanField(default=False)

# views.py

for book in books:
        in_library_users_set = set(book.in_library.all())
        book.common_in_library_members = []
        book.request_user_kbook_slug = None # Initialise le slug pour l'utilisateur actuel

        # Vérifie si request.user est dans in_library et owner d'un CustomBook pour ce livre
        if request.user in in_library_users_set:
            user_kbook_for_request_user = CustomBook.objects.filter(book=book, owner=request.user).first()
            if user_kbook_for_request_user:
                book.request_user_kbook_slug = user_kbook_for_request_user.slug

        for user in in_library_users_set.intersection(common_members_set):
            
            user_kbook = CustomBook.objects.filter(book=book, owner=user).first()
            book.common_in_library_members.append({
                'user': user,
                'kbook_slug': user_kbook.slug if user_kbook else None,
                'kbook_borrowing': user_kbook.borrowing if user_kbook.borrowing.status == "on_going" else None
            })

# html

