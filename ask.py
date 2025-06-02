J'ai deux filtres: un pour filtrer le statut de lecture, qui est associé au modèle Book et qui fonctionne bien. 
J'ai un deuxième filtre pour filtrer le statut d'emprunt qui est associé au modèle Custom Book. Comment lier les deux filtres ? 

#views.py

books_reset = books
    
    borrow_status = "all_borrow_status"
    borrow_status_description = _("All Borrow Status")
    reading_status = "all_status"
    reading_status_description = _("All Reading Status")
    search_query = ""

    

    if request.method == "POST":

        if "filter" in request.POST:
            
            reading_status = request.POST.get('reading-status')
            borrow_status = request.POST.get('borrow-status')   
            search_query = request.POST["search_query"].lower()
            
            search_queryset = []

            for book in books:
                if search_query in book.title.lower():
                    search_queryset.append(book)
                elif search_query in book.author.lower():
                    search_queryset.append(book)
            
            books = search_queryset
            
            queryset = []
                
            for book in books:
                if reading_status == "all_status":
                    queryset = books
                    reading_status_description = _("All Reading Status")
                elif reading_status == "is_read":
                    reading_status_description = _("Read")
                    if request.user in book.readers.all():
                        queryset.append(book)
                elif reading_status == "is_reading":
                    reading_status_description = _("Reading it")
                    if request.user in book.readings.all():
                        queryset.append(book)
                elif reading_status == "in_wish":
                    
                    reading_status_description = _("Want to read")
                    if request.user in book.in_whishlist.all():
                        queryset.append(book)
                elif reading_status == "no_read":
                    reading_status_description = _("Not read yet")
                    if request.user in book.no_read.all():
                        queryset.append(book)
                elif reading_status == "wont_read":
                    reading_status_description = _("No intention to read it")
                    if request.user in book.wont_read.all():
                        queryset.append(book)
                elif reading_status == "give_up":
                    reading_status_description = _("Given up")
                    if request.user in book.give_up.all():
                        queryset.append(book)

            
            books = queryset
            queryset_2 = []
            if borrow_status == "all_borrow_status":
                    queryset_2 = queryset
                    borrow_status_description=_("All borrow status")
            else:
                for kbook in queryset:           
                    if borrow_status == "is_borrowed_by_user":
                        borrow_status_description=_("Currently borrowed by me")
                        if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = "on_going").exists():
                            queryset_2.append(kbook)
                    elif borrow_status == "reserved_by_me":
                        borrow_status_description=_("Reserved by me")
                        if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = "pending").exists():
                            queryset_2.append(kbook)
                    elif borrow_status == "borrowable":
                        borrow_status_description=_("Borrowable")
                        if kbook.is_disponible == True and kbook.owner != request.user: 
                            queryset_2.append(kbook)
                    elif borrow_status == "is_on_loan":
                        borrow_status_description=_("On Loan")
                        if Borrow.objects.filter(custom_book = kbook, status="on_going").exists() and kbook.owner == request.user:
                            queryset_2.append(kbook)
                    elif borrow_status == "with_reservations":
                        borrow_status_description=_("Reservations asked to me")
                        if Borrow.objects.filter(custom_book = kbook, status="pending").exists() and kbook.owner == request.user:
                            queryset_2.append(kbook)
            

            #unique_kbooks = queryset_2
            books = queryset_2

        
            
                
        if "reset" in request.POST:
            books = books_reset
            borrow_status = "all_borrow_status"
            borrow_status_description = _("All Borrow Status")
            reading_status = "all_status"
            reading_status_description = _("All Reading Status")
            
    
    
    books = books

#models.py 

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
    