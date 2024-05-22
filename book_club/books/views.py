import json
import environ
import ssl
import os
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from urllib.request import urlopen
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from .forms import BookSearch, AddMeetingForm, AddCommentForm, AddCustomBookForm
from groups.models import CustomGroup
from .models import Book, Meeting, CustomBook, Comment, Borrow, BookTag
from users.models import CustomUser

tz= timezone.get_current_timezone()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

MESSAGE_BOOK_REGISTERED = _(
    "The book is already registered here."
)

# Functions
def book_search(search):
    api = "https://www.googleapis.com/books/v1/volumes?q=search:"
  
    search = search
    
    if (search == False) or (search == ""):
            return redirect('book-search')

    search = search.replace(' ', '+')
    
    r = urlopen(api + search, context=ctx)
    
    data = json.load(r)
    
   
    books=[]
    if data["totalItems"] > 0:
        
        fetched_books = data['items']
    

        
        for book in fetched_books:
            book_dict = {
                'title': book['volumeInfo']['title'],
                'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "/static/assets/img/illustrations/book-placeholder.jpeg",
                'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
                'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
                'info': book['volumeInfo']['infoLink'],
                'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0,
                'isbn': book['volumeInfo']['industryIdentifiers'][0]['identifier'] if 'industryIdentifiers' in book['volumeInfo'] else 0,
            }
            books.append(book_dict)
    
    else:
        print("no items")

    return books

def book_save(request, id):
    api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
  
    isbn = id
  
    r = urlopen(api + isbn, context=ctx)
    
    book_data = json.load(r)
  # if r.status_code != 200:
  #     return render(request, 'books/book-results.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

  # data = r.json()
    
    volume_info = book_data["items"][0]["volumeInfo"]
    

  
    book={}
 
    book = {
        'title': volume_info['title'],
        'cover': volume_info['imageLinks']['thumbnail'] if 'imageLinks' in volume_info else "/static/assets/img/illustrations/book-placeholder.jpeg",
        'authors': ", ".join(volume_info['authors']) if 'authors' in volume_info else _("Unknown Authors"),
        'pages': volume_info['pageCount'] if 'pageCount' in volume_info else 0,
        'main_category': volume_info['mainCategory'] if 'mainCategory' in volume_info else None,
        'categories': volume_info['categories'][0] if 'categories' in volume_info else None,
        'language': volume_info['language'] if 'language' in volume_info else None,
        'publisher': volume_info['publisher'] if 'publisher' in volume_info else None,
        'publishDate': volume_info['publishedDate'] if 'publishedDate' in volume_info else None,
        'description': volume_info['description'] if 'description' in volume_info else None,
        'isbn': volume_info['industryIdentifiers'][0]['identifier'] if 'industryIdentifiers' in volume_info else volume_info['isbn'],
        
    }

    return book

def book_add(request, book_in_db, groups, picture):
    for i in groups:
        group = CustomGroup.objects.get(uuid=i)
        if group in book_in_db.groups.all() and group.group_type == 'one_book':
            messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
        elif group in book_in_db.groups.all() and group.group_type == 'library':
            messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
        elif group in book_in_db.groups.all() and group.group_type == 'wishlist':
            messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
        elif group in book_in_db.groups.all() and group.group_type == 'several_books' and CustomBook.objects.filter(book = book_in_db, owner = request.user).exists():
            messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
        else:
            book_in_db.groups.add(group)
            new_kbook = CustomBook(book=book_in_db, group=group)
            if picture:
                new_kbook.picture = picture
            if group.group_type == 'library':
                new_kbook.owner = request.user
                new_kbook.save()
                book_in_db.in_library.add(request.user)
                if CustomBook.objects.filter(book = book_in_db, admin = request.user, group__group_type = 'wishlist').exists():
                    old_whislist = CustomBook.objects.get(book = book_in_db, admin = request.user, group__group_type = 'wishlist')
                    book_in_db.groups.remove(old_whislist.group)
                    book_in_db.in_wishlist.remove(request.user)
                    old_whislist.delete() 
                    
            elif group.group_type == 'several_books':
                if CustomBook.objects.filter(book = book_in_db, owner = request.user, group__group_type = 'library').exists():
                    new_kbook = get_object_or_404(CustomBook, book=book_in_db, owner=request.user, group__group_type = 'library')
                    new_kbook.sharing_groups.add(group)
                    new_kbook.is_borrowable = True
                    new_kbook.is_disponible = True 
                    new_kbook.save()
                else:
                    new_kbook.save()
                    new_kbook.sharing_groups.add(group)
                    library=get_object_or_404(CustomGroup, group_type="library", leader=request.user)
                    new_kbook.owner = request.user
                    new_kbook.group = library
                    new_kbook.is_borrowable = True
                    new_kbook.is_disponible = True
                    book_in_db.in_library.add(request.user)
                    book_in_db.groups.add(library)
                    new_kbook.save()
            else:
                new_kbook.admin = request.user
                if group.group_type == "wishlist":
                    book_in_db.in_wishlist.add(request.user)
                new_kbook.save()
    book_in_db.save()

    if CustomBook.objects.filter(book=book_in_db, owner=request.user, group__group_type = 'library').exists() and CustomBook.objects.filter(book=book_in_db, admin=request.user,group__group_type = 'wishlist').exists():
        book_in_db.in_wishlist.add(request.user)
        book_to_remove = CustomBook.objects.get(book=book_in_db, admin=request.user, group__group_type = 'wishlist')
        book_in_db.groups.remove(book_to_remove.group)
        book_to_remove.delete()

        


# BOOK VIEWS
@login_required
def add_book(request, id):
    book_in_db = None
    kgroups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    
    try:
        book=book_save(request, id)
    except:
        messages.error(request, _('There was an error in the interpretation of result : please add the book yourself.'))
        return redirect('add-book-custom')
   
    
    context = {
        'kgroups':kgroups,
        'book':book,
    }

    if Book.objects.filter(isbn=id).exists():
        book_in_db = Book.objects.get(isbn=id)
    else:
        book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
        book_in_db.save()
    
    


    if request.method=='POST':
        groups = request.POST.getlist('group')
        
        if len(groups) == 0:
            messages.error(request, _('You have to choose where to register this book.'))
        else:
            book_add(request, book_in_db, groups, picture=None)
            
            return redirect('all-books')
    
    return render(request, 'books/book-search-detail.html', context)

@login_required
def add_custom_book(request):
    form = AddCustomBookForm(request.user)
    kgroups = CustomGroup.objects.filter(members__id__contains=request.user.id)

    
    

    if request.method == 'POST':
        form = AddCustomBookForm(request.user, request.POST, request.FILES)
        if form.is_valid():
                groups = request.POST.getlist('group')
                if len(groups) == 0:
                    messages.error(request, _('You have to choose where to register this book.'))
                else:
                    picture = request.FILES.get('picture')
                    book=form.save(commit=False)
                    book_in_db = Book(title=book.title, author=book.author, isbn=book.isbn, description=book.description, pages=book.pages)
                    book_in_db.save()

                    book_add(request, book_in_db, groups, picture)
                    
                    return redirect('all-books')
                
            
        else:
            print(form.errors)
     

    return render(request, 'books/add-edit-book.html', {'form': form, 'kgroups': kgroups})

@login_required
def new_book_search(request):
    if request.method == 'GET':
        form = BookSearch()
        return render(request, 'books/search.html', {'form': form})
    else:
        form = BookSearch(request.POST)
        if form.is_valid():
            search = request.POST.get('search', False)
            
            try:
                books=book_search(search)
                if len(books) == 0:
                    messages.error(request, _('There was an error in the interpretation of result : please add the book yourself.'))
                    return redirect('add-book-custom')
                else:
                    return render(request, 'books/search.html', {'form': form, 'books': books})
            except Exception as e:
                print(e)
                messages.error(request, _('Invalid search. Try without any accent.'))
                return render(request, 'books/search.html', {'form': form})
         
                
            

@login_required
def search_book_for_meeting(request, id):
    meeting = Meeting.objects.get(id=id)
    if request.method == 'GET':
        form = BookSearch()
        return render(request, 'books/search.html', {'form': form})
    else:
        form = BookSearch(request.POST)
        if form.is_valid():
            search = request.POST.get('search', False)
            books = book_search(search)
            return render(request, 'books/search.html', {'form': form, 'books': books, 'meeting':meeting})
        
@login_required
def add_new_book_to_group(request,slug, isbn):
    group = CustomGroup.objects.get(slug=slug)
    book_in_db = None
    book_in_group = False
    book=book_save(request, isbn)
    
    context = {
        'group': group,
        'book':book,
    }

    if Book.objects.filter(isbn=isbn).exists():
        book_in_db = Book.objects.get(isbn=isbn)
        if book_in_db in group.books:
            book_in_group = True

    if request.method=='POST':
        if book_in_db:
            if book_in_group:
                messages.warning(request, _(f'Book already in group'))
            else:
                book_in_db.groups.add(group)
                book_in_db.save()
                new_kbook = CustomBook(book=book_in_db, group=group, admin=request.user)
                new_kbook.save()
           
        else:
            new_book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
            new_book_in_db.save()
            new_book_in_db.groups.add(group)
            new_book_in_db.save()
            new_kbook = CustomBook(book=new_book_in_db, group=group, admin=request.user)
            new_kbook.save()
            
        
        return redirect('group-detail', group.slug)
    
    return render(request, 'books/book-search-detail.html', context)

@login_required
def add_new_book_to_meeting(request,id, isbn):
    meeting = Meeting.objects.get(id=id)
    group = meeting.group
    book_in_db = None
    book=book_save(request,isbn)
    
    context = {
        'meeting': meeting,
        'book':book,
    }

    if Book.objects.filter(isbn=isbn).exists():
        book_in_db = Book.objects.get(isbn=isbn)
    else:
        book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
        book_in_db.save()

    if request.method=='POST':
        #if book_in_db:
            if group in book_in_db.groups.all():
                kbook = CustomBook.objects.get(book=book_in_db, group=group)
                meeting.book = kbook
            else:
                print("pas dans la db")
                book_in_db.groups.add(group)
                book_in_db.save()
                new_kbook = CustomBook(book=book_in_db, group=group, admin=request.user)
                new_kbook.save()
                meeting.book=new_kbook
           

        # else:
            
        #     new_book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
        #     new_book_in_db.save()
        #     new_book_in_db.groups.add(group)
        #     new_book_in_db.save()
        #     new_kbook = CustomBook(book=new_book_in_db, group=group, admin=request.user)
        #     new_kbook.save()
        #     meeting.book = new_kbook
        

            meeting.save()
            return redirect('group-detail', group.slug)
    
    return render(request, 'books/book-search-detail.html', context)

@login_required
def book_detail(request, slug):
    user = request.user
    
    kbook = get_object_or_404(CustomBook, slug=slug)
    book = kbook.book 
    
    groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    groups_of_book = book.groups.filter(members__id__contains=request.user.id)
    print(groups_of_book)

    all_reviews = Comment.objects.filter(book=book)
    #filter by groups
    
    author_filter = Q()
    for group in groups:
        author_filter |= Q(author__group_members = group)

    group_reviews = all_reviews.filter(author_filter).distinct()

    if kbook.group.group_type == 'one_book':
        if CustomBook.objects.filter(book=book, owner=user).exists():
            kbook = get_object_or_404(CustomBook, book=book, owner=user)
        elif CustomBook.objects.filter(book=book, group__group_type = "several_books").exists():
            sharable_kbooks = CustomBook.objects.filter(book=book, group__group_type = "several_books", owner=author_filter)
            kbook = sharable_kbooks.first()
            
            

    
    is_read = False
    is_reading = False
    in_wish = False
    no_read = False
    wont_read = False
    give_up = False
    in_library = False

    if user in book.readers.all():
        is_read = True
    elif user in book.readings.all():
        is_reading = True
    elif user in book.in_wishlist.all():
        in_wish = True
    elif user in book.no_read.all():
        no_read = True
    elif user in book.wont_read.all():
        wont_read = True
    elif user in book.give_up.all():
        give_up = True
    
    if user in book.in_library.all():
        in_library = True



    

    sharing_groups = CustomGroup.objects.filter(members__id__contains=user.id, group_type="several_books")
    available_sharing_groups = []
    if CustomBook.objects.filter(book=book, owner=user).exists():
        for group in sharing_groups:
            if CustomBook.objects.filter(book=book, sharing_groups__id__contains=group.id, owner=user).exists():
                pass
            else:
                available_sharing_groups.append(group)   

    #toggle borroawable

    if request.method == 'POST':
        # book_id = request.POST.get('book_id')
        # kbook = get_object_or_404(CustomBook, id=book_id)

        if kbook.is_borrowable == True:
            kbook.is_borrowable = False
            kbook.is_disponible = False
            kbook.save()
            return redirect('book-detail', kbook.slug)
        else:
            kbook.is_borrowable = True
            if Borrow.objects.filter(custom_book=kbook, status="on_going").exists():
                kbook.is_disponible = False
            else:
                kbook.is_disponible = True
        kbook.save()
        return redirect('book-detail', kbook.slug)

    #tags
    tags = BookTag.objects.filter(kbooks__id__contains = kbook.id).distinct()
        
    #borrows
    
    is_reserved_by_user = False
    is_borrowed_by_user = False
    common_sharing_groups = []
    borrows = None
    reservations = None
    
    for group in kbook.sharing_groups.all():
        if user in group.members.all():
            common_sharing_groups.append(group)
    
    

    borrows = Borrow.objects.filter(custom_book = kbook, status = 'on_going') | Borrow.objects.filter(custom_book = kbook, status = 'returned', need_return_confirmation = True)
    if Borrow.objects.filter(custom_book = kbook, status = 'on_going', borrower=request.user).exists():
        is_borrowed_by_user = True
    elif Borrow.objects.filter(custom_book = kbook, status = 'returned', need_return_confirmation = True, borrower = request.user).exists():
        is_borrowed_by_user = True
    reservations = Borrow.objects.filter(custom_book = kbook, status = 'pending')
    if Borrow.objects.filter(custom_book = kbook, status="pending", borrower=user):
        is_reserved_by_user = True

    
    #read_by
    readers = []
    for group in groups_of_book:
        for member in group.members.all():
            if member in book.readers.all():
                readers.append(member)

    




    

    context = {
        'book': kbook,
        'is_read': is_read,
        'is_reading': is_reading,
        'in_wish': in_wish,
        'no_read':no_read,
        'wont_read':wont_read,
        'give_up':give_up,
        'in_library':in_library,
        'all_reviews':all_reviews,
        'group_reviews':group_reviews,
        'sharing_groups' :sharing_groups,
        'available_sharing_groups':available_sharing_groups,
        'groups_of_book':groups_of_book,
        'common_sharing_groups':common_sharing_groups,
        'is_borrowed_by_user':is_borrowed_by_user,
        'borrows':borrows,
        'reservations':reservations,
        'is_reserved_by_user':is_reserved_by_user,
        'readers':readers,
        'tags':tags,
        
        
        }

    return render(request, 'books/book-detail.html', context)

@login_required
def edit_reading_status(request, slug, id):
    book = get_object_or_404(Book, slug=slug)
    user = request.user
    kbook = get_object_or_404(CustomBook, id=id)

    is_read = False
    is_reading = False
    in_wish = False
    no_read = False
    wont_read = False
    give_up = False
    

    if user in book.readers.all():
        is_read = True
    elif user in book.readings.all():
        is_reading = True
    elif user in book.in_wishlist.all():
        in_wish = True
    elif user in book.no_read.all():
        no_read = True
    elif user in book.wont_read.all():
        wont_read = True
    elif user in book.give_up.all():
        give_up = True

    context = {
        'book': book,
        'kbook': kbook,
        'is_read': is_read,
        'is_reading': is_reading,
        'in_wish': in_wish,
        'no_read':no_read,
        'wont_read':wont_read,
        'give_up':give_up,
    }

    if request.method=="POST":
        reading_status = request.POST.get('reading-status')
        print(reading_status)
        if reading_status == "is_read":
            if is_read == False:
                book.readers.add(user)
                if is_reading:
                    book.readings.remove(user)
                elif in_wish:
                    book.in_wishlist.remove(user)
                elif no_read:
                    book.no_read.remove(user)
                elif wont_read:
                    book.wont_read.remove(user)
                elif give_up:
                    book.give_up.remove(user)

        if reading_status == "in_wish":
            if in_wish == False:
                book.in_wishlist.add(user)
                if is_reading:
                    book.readings.remove(user)
                elif is_read:
                    book.readers.remove(user)
                elif no_read:
                    book.no_read.remove(user)
                elif wont_read:
                    book.wont_read.remove(user)
                elif give_up:
                    book.give_up.remove(user)

        if reading_status == "is_reading":
            if is_reading == False:
                book.readings.add(user)
                if in_wish:
                    book.in_wishlist.remove(user)
                elif is_read:
                    book.readers.remove(user)
                elif no_read:
                    book.no_read.remove(user)
                elif wont_read:
                    book.wont_read.remove(user)
                elif give_up:
                    book.give_up.remove(user)

        if reading_status == "no_read":
            if no_read == False:
                book.no_read.add(user)
                if in_wish:
                    book.in_wishlist.remove(user)
                elif is_read:
                    book.readers.remove(user)
                elif is_reading:
                    book.readings.remove(user)
                elif wont_read:
                    book.wont_read.remove(user)
                elif give_up:
                    book.give_up.remove(user)

        if reading_status == "wont_read":
            if wont_read == False:
                book.wont_read.add(user)
                if in_wish:
                    book.in_wishlist.remove(user)
                elif is_read:
                    book.readers.remove(user)
                elif is_reading:
                    book.readings.remove(user)
                elif no_read:
                    book.no_read.remove(user)
                elif give_up:
                    book.give_up.remove(user)

        if reading_status == "give_up":
            if give_up == False:
                book.give_up.add(user)
                if in_wish:
                    book.in_wishlist.remove(user)
                elif is_read:
                    book.readers.remove(user)
                elif is_reading:
                    book.readings.remove(user)
                elif no_read:
                    book.no_read.remove(user)
                elif wont_read:
                    book.wont_read.remove(user)

        return redirect('book-detail', kbook.slug)

    return render(request, 'books/edit-reading-status.html', context)

@login_required
def edit_book(request, slug):
    book = get_object_or_404(CustomBook, slug=slug)
    form = AddCustomBookForm(request.user, instance = book)
    

    if request.method == 'POST':
        form = AddCustomBookForm(request.user, request.POST, request.FILES, instance=book)
        if form.is_valid():
                picture = request.FILES.get('picture')
                book.picture = picture
                book.save()
                
                    

               
                
                return redirect('book-detail', book.slug)
            
        else:
            print(form.errors)
     

    return render(request, 'books/add-edit-book.html', {'form': form, 'book': book})

@login_required
def all_books(request):
    user_groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    common_members = []

    for group in user_groups:
        for member in group.members.all():
            common_members.append(member)
    common_members = set(common_members)
    print(common_members)
     
    # books = Book.objects.filter(groups__in=user_groups).distinct()
    # kbooks= CustomBook.objects.filter(book__in=books)
    kbooks = CustomBook.objects.filter(owner__in=common_members) | CustomBook.objects.filter(admin__in=common_members)
  

    print(kbooks)

    
    members_kbooks = []
    owned_kbooks_isbn = []
    non_sharable_kbooks_isbn = []
    unique_kbooks = []
    

    
    for kbook in kbooks:
        if kbook.isbn != None:
            if kbook.owner == None and kbook.admin in common_members:
                non_sharable_kbooks_isbn.append(kbook.isbn)
                members_kbooks.append(kbook)
            elif kbook.owner != None and kbook.owner in common_members:
                owned_kbooks_isbn.append(kbook.isbn)
                members_kbooks.append(kbook)
        else:
            if kbook.owner == None and kbook.admin in common_members:
                non_sharable_kbooks_isbn.append(kbook.title)
                members_kbooks.append(kbook)
            elif kbook.owner != None and kbook.owner in common_members:
                owned_kbooks_isbn.append(kbook.title)
                members_kbooks.append(kbook)

        

    for kbook in members_kbooks:
        if (kbook.isbn in owned_kbooks_isbn and kbook.isbn in non_sharable_kbooks_isbn) or (kbook.title in owned_kbooks_isbn and kbook.title in non_sharable_kbooks_isbn):
            if kbook.owner != None:
                unique_kbooks.append(kbook)
        elif (kbook.isbn in owned_kbooks_isbn and kbook.isbn not in non_sharable_kbooks_isbn) or (kbook.title in owned_kbooks_isbn and kbook.title not in non_sharable_kbooks_isbn) :
            if kbook.owner == request.user or (kbook.owner != request.user and kbook.is_borrowable == True):
                unique_kbooks.append(kbook)
        elif (kbook.isbn in non_sharable_kbooks_isbn and kbook.isbn not in owned_kbooks_isbn) or (kbook.title in non_sharable_kbooks_isbn and kbook.title not in owned_kbooks_isbn) :
            unique_kbooks.append(kbook)

    unique_kbooks_reset = unique_kbooks
    
    borrow_status = "all_borrow_status"
    borrow_status_description = _("All Borrow Status")
    reading_status = "all_status"
    reading_status_description = _("All Reading Status")

   

    if request.method == "POST":
        
        

        if "filter" in request.POST:
            
            reading_status = request.POST.get('reading-status')
            borrow_status = request.POST.get('borrow-status')   
            
            queryset = []
                
            for kbook in unique_kbooks:
                print(kbook)
                if reading_status == "all_status":
                    queryset = unique_kbooks
                    reading_status_description = _("All Reading Status")
                elif reading_status == "is_read":
                    reading_status_description = _("Read")
                    if request.user in kbook.book.readers.all():
                        queryset.append(kbook)
                elif reading_status == "is_reading":
                    reading_status_description = _("Reading it")
                    if request.user in kbook.book.readings.all():
                        queryset.append(kbook)
                elif reading_status == "in_wish":
                    reading_status_description = _("Want to read")
                    if request.user in kbook.book.in_wishlist.all():
                        queryset.append(kbook)
                elif reading_status == "no_read":
                    reading_status_description = _("Not read yet")
                    if request.user in kbook.book.no_read.all():
                        queryset.append(kbook)
                elif reading_status == "wont_read":
                    reading_status_description = _("No intention to read it")
                    if request.user in kbook.book.wont_read.all():
                        queryset.append(kbook)
                elif reading_status == "give_up":
                    reading_status_description = _("Given up")
                    if request.user in kbook.book.give_up.all():
                        queryset.append(kbook)

            print(queryset)

            queryset_2 = []
            if borrow_status == "all_borrow_status":
                    queryset_2 = queryset
                    borrow_status_description=_("All borrow status")
            else:
                for kbook in queryset:           
                    if borrow_status == "is_borrowed_by_user":
                        borrow_status_description=_("Actually borrowed by me")
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
            

            unique_kbooks = queryset_2
              
            
                
        if "reset" in request.POST:

            unique_kbooks = unique_kbooks_reset
            borrow_status = "all_borrow_status"
            borrow_status_description = _("All Borrow Status")
            reading_status = "all_status"
            reading_status_description = _("All Reading Status")
            
    

    context = {
        
        'kbooks': kbooks,
        'unique_kbooks': unique_kbooks,
        'reading_status': reading_status,
        'borrow_status': borrow_status,
        'reading_status_description':reading_status_description,
        'borrow_status_description': borrow_status_description,
        
    }
    return render(request, 'books/all-books.html', context)

@login_required
def group_books(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    user_groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    common_members = []

    for kgroup in user_groups:
        for member in kgroup.members.all():
            common_members.append(member)
    common_members = set(common_members)

    print(group)
    
    kbooks = CustomBook.objects.filter(owner__in=common_members) | CustomBook.objects.filter(admin__in=common_members)
    unique_kbooks = []
    if group.group_type == 'several_books':
        
        unique_kbooks = CustomBook.objects.filter(sharing_groups__id__contains = group.id)
        
    elif group.group_type == 'wishlist':
        for kbook in kbooks:
            if request.user in kbook.book.in_wishlist.all():
                unique_kbooks.append(kbook)

    else:
        unique_kbooks = CustomBook.objects.filter(group=group)

    unique_kbooks_reset = unique_kbooks
    borrow_status = "all_borrow_status"
    borrow_status_description = _("All Borrow Status")
    reading_status = "all_status"
    reading_status_description = _("All Reading Status")
    
    
    if request.method == 'POST':
        if "filter" in request.POST:
            
            reading_status = request.POST.get('reading-status')
            borrow_status = request.POST.get('borrow-status')   
            
            queryset = []
                
            for kbook in unique_kbooks:
                print(kbook)
                if reading_status == "all_status":
                    queryset = unique_kbooks
                    reading_status_description = _("All Reading Status")
                elif reading_status == "is_read":
                    reading_status_description = _("Read")
                    if request.user in kbook.book.readers.all():
                        queryset.append(kbook)
                elif reading_status == "is_reading":
                    reading_status_description = _("Reading it")
                    if request.user in kbook.book.readings.all():
                        queryset.append(kbook)
                elif reading_status == "in_wish":
                    reading_status_description = _("Want to read")
                    if request.user in kbook.book.in_wishlist.all():
                        queryset.append(kbook)
                elif reading_status == "no_read":
                    reading_status_description = _("Not read yet")
                    if request.user in kbook.book.no_read.all():
                        queryset.append(kbook)
                elif reading_status == "wont_read":
                    reading_status_description = _("No intention to read it")
                    if request.user in kbook.book.wont_read.all():
                        queryset.append(kbook)
                elif reading_status == "give_up":
                    reading_status_description = _("Given up")
                    if request.user in kbook.book.give_up.all():
                        queryset.append(kbook)

            print(queryset)

            queryset_2 = []
            if borrow_status == "all_borrow_status":
                    queryset_2 = queryset
                    borrow_status_description=_("All borrow status")
            else:
                for kbook in queryset:           
                    if borrow_status == "is_borrowed_by_user":
                        borrow_status_description=_("Actually borrowed by me")
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
            

            unique_kbooks = queryset_2
              
            
                
        if "reset" in request.POST:

            unique_kbooks = unique_kbooks_reset
            borrow_status = "all_borrow_status"
            borrow_status_description = _("All Borrow Status")
            reading_status = "all_status"
            reading_status_description = _("All Reading Status")
    
    context = {'unique_kbooks': unique_kbooks,
               'group': group,
               'reading_status': reading_status,
                'borrow_status': borrow_status,
                'reading_status_description':reading_status_description,
                'borrow_status_description': borrow_status_description,
               }
    
    return render(request, 'books/all-books.html', context)

@login_required
def pass_book_to_library(request,slug):
    kbook = get_object_or_404(CustomBook, slug=slug)
    book = kbook.book
    groups = CustomGroup.objects.filter(members__id__contains = request.user.id, group_type = "library")

    context = {'groups': groups,
               'book': book,
               'kbook':kbook}

    if request.method == 'POST':
        groups = request.POST.getlist('group')
        if len(groups) == 0:
            messages.error(request, _('You have to choose where to register this book.'))
        else:
            for i in groups:
                group = CustomGroup.objects.get(uuid=i)
                
                if group in book.groups.all():
                    messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
                else:
                    if kbook.group.group_type == 'wishlist':
                        book.groups.remove(kbook.group)
                        kbook.group = group
                        kbook.owner = request.user
                    else:
                        kbook = CustomBook(book=book, owner = request.user, group = group)
                    book.groups.add(group)
                    book.in_library.add(request.user)
                    kbook.save()
                

                    
            book.save()
            return redirect('book-detail', kbook.slug)
    
    return render(request, 'books/pass-book-to-sharing-club.html', context=context)

@login_required
def pass_book_to_sharing_group(request, slug):
    kbook = get_object_or_404(CustomBook, slug=slug)
    book = kbook.book
    groups = CustomGroup.objects.filter(members__id__contains = request.user.id, group_type = "several_books")

    context = {'groups': groups,
               'book': book,
               'kbook':kbook}

    if request.method == 'POST':
        groups = request.POST.getlist('group')
        if len(groups) == 0:
            messages.error(request, _('You have to choose where to share this book.'))
        else:
            for i in groups:
                group = CustomGroup.objects.get(uuid=i)
                
                if group in kbook.sharing_groups.all():
                    messages.error(request, MESSAGE_BOOK_REGISTERED, group.kname)
                else:
                    book.groups.add(group)
                    kbook.sharing_groups.add(group)
                    kbook.is_borrowable = True
                    if Borrow.objects.filter(custom_book = kbook, status="on_going").exists():
                        kbook.is_disponible = False
                    else:
                        kbook.is_disponible = True
                    kbook.save()
                    
            book.save()
            return redirect('book-detail', kbook.slug)

    return render(request, 'books/pass-book-to-sharing-club.html', context=context)
    
@login_required
def delete_book_from_group(request,slug):
    book = get_object_or_404(Book, slug=slug)
    user_kbooks = CustomBook.objects.filter(book=book, owner=request.user) | CustomBook.objects.filter(book=book, admin=request.user)
    
            
    context = {'user_kbooks': user_kbooks,
               }

    return render(request, 'books/delete-book.html', context=context)

@login_required
def delete_book(request, slug):
    kbook = CustomBook.objects.get(slug=slug)
    book = kbook.book
    book.groups.remove(kbook.group)
    if kbook.picture:
        os.remove(kbook.picture.path)
        kbook.picture.delete()
    kbook.delete()
    if kbook.group.group_type == 'library':
        book.in_library.remove(request.user)
       
    return redirect('group-books', kbook.group.slug)

@login_required
def delete_book_from_sharing_group(request, id, slug):
    kbook = get_object_or_404(CustomBook, id=id)
    group = get_object_or_404(CustomGroup, slug=slug)

    kbook.sharing_groups.remove(group)
    kbook.book.groups.remove(group)

    return redirect('group-books', group.slug)


@login_required
def toggle_exchange(request, id):
    kbook = get_object_or_404(CustomBook, id=id)
    if kbook.is_borrowable == True:
        kbook.is_borrowable = False
        kbook.is_disponible = False
        kbook.save()
        return redirect('book-detail', kbook.slug)
    else:
        kbook.is_borrowable = True
        if Borrow.objects.filter(custom_book=kbook, status="on_going").exists():
            kbook.is_disponible = False
        else:
            kbook.is_disponible = True
    kbook.save()
    return redirect('book-detail', kbook.slug)

#TAGS

@login_required
def add_book_tags(request, slug):
    kbook = get_object_or_404(CustomBook, slug=slug)
    kbook_tags = BookTag.objects.filter(kbooks__id__contains=kbook.id)
    tags = BookTag.objects.filter(author=kbook.owner)

    context = {
        'kbook': kbook,
        'kbook_tags': kbook_tags,
        'tags': tags
    }

    if request.method == 'POST':
        if "add-tag" in request.POST:
            name = request.POST.get("tag-name")
            tag_color = request.POST.get("tag-color")

            new_tag = BookTag(author=request.user, name=name, color=tag_color)
            new_tag.save()
            new_tag.kbooks.add(kbook)
            new_tag.save()
            return redirect('add-book-tags', kbook.slug)
            

        if "select-tags" in request.POST:
            tags = request.POST.getlist(('tag'))
            print(tags)
            #remove tags
        
            for tag in kbook_tags:
                if tag not in tags:
                    tag.kbooks.remove(kbook)

            #add tags                                          
            for tag in tags:
                book_tag = get_object_or_404(BookTag, id=tag)
                if tag not in kbook_tags:
                    book_tag.kbooks.add(kbook)
                    book_tag.save()

            return redirect('book-detail', kbook.slug)

    return render(request, 'books/add-edit-tags.html', context=context)

#REVIEWS

@login_required
def add_review(request, slug):
    kbook=get_object_or_404(CustomBook, slug=slug)
    book = kbook.book
    form=AddCommentForm()

    if request.method=='POST':
        form=AddCommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.book=book
            comment.author=request.user
            comment.save()
            book.readers.add(request.user)
            book.save()
            return redirect('book-detail', kbook.slug)

    return render(request, "books/add-comment.html", {'form':form, 'book':book, 'kbook':kbook})

@login_required
def edit_review(request, id):
    review = get_object_or_404(Comment, id=id)
    all_kbooks = CustomBook.objects.filter(book=review.book)
    #filter by groups
    user_groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    user_kbooks = []
    for kbook in all_kbooks:
        if kbook.group in user_groups:
            user_kbooks.append(kbook)

    book = user_kbooks[0]

    form = AddCommentForm(instance=review)

    if request.method=='POST':
        form=AddCommentForm(request.POST, instance=review)
        if form.is_valid():
            review=form.save()
            return redirect('book-detail', book.slug)
        
    return render(request, "books/add-comment.html", {'form':form, 'book':book, 'review':review})

@login_required
def delete_review(request, id):
    review = get_object_or_404(Comment, id=id)
    all_kbooks = CustomBook.objects.filter(book=review.book)
    #filter by groups
    user_groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    user_kbooks = []
    for kbook in all_kbooks:
        if kbook.group in user_groups:
            user_kbooks.append(kbook)

    book = user_kbooks[0]
    review.delete()

    return redirect('book-detail', book.slug)

#MEETINGS   
     
@login_required
def add_meeting(request, slug):
    group = CustomGroup.objects.get(slug=slug)
    books = Book.objects.filter(groups__id__contains = group.id)
    form = AddMeetingForm()

    if request.method == 'POST':
        form = AddMeetingForm(request.POST)
        meeting_at = request.POST.get('meeting_at')
        if form.is_valid():
            print("form validation successful")
            if "search-book" in request.POST:
                meeting = form.save()
                if meeting_at:
                    meeting.meeting_at = meeting_at
                else:
                    meeting.meeting_at = meeting.meeting_at
                meeting.group = group
                meeting.save()
                return redirect('search-book-for-meeting', meeting.id)
            elif "add-meeting" in request.POST:
                print("add meeting")
                meeting = form.save()
                if meeting_at:
                    meeting.meeting_at = meeting_at
                else:
                    meeting.meeting_at = None
                meeting.group = group
                meeting.save()
                return redirect('group-detail', group.slug)
        else:
            print(form.errors)

    context = {'form': form,
               'group': group,
                'books':books, }
    
    return render(request, "books/meetings/add-meeting.html", context=context)

@login_required
def edit_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id)
    book = meeting.book
    group = meeting.group
    form = AddMeetingForm(instance=meeting)
    

    if request.method == 'POST':
        form = AddMeetingForm(request.POST, instance=meeting)
        meeting_at = request.POST.get('meeting_at')
        if form.is_valid():
            if "search-book" in request.POST:
                meeting = form.save()
                if meeting_at:
                    meeting.meeting_at = meeting_at
                else:
                    meeting.meeting_at = meeting.meeting_at
                meeting.save()
                return redirect('search-book-for-meeting', meeting.id)
            elif "add-meeting" in request.POST:
                print("add meeting")
                meeting = form.save()
                if meeting_at:
                    meeting.meeting_at = meeting_at
                else:
                    meeting.meeting_at = meeting.meeting_at
                meeting.group = group
                meeting.save()
                return redirect('group-detail', group.slug)
            
        else:
            print(form.errors)

    context = {'form': form,
               'meeting': meeting,
                'book':book, 
                'group':group}
    
    return render(request, "books/meetings/add-meeting.html", context=context)

@login_required
def delete_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id)
    group = meeting.group
    meeting.delete()

    return redirect('group-detail', group.slug)

#BORROW


@login_required
def borrow_book_within_group(request, id, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    kbook = get_object_or_404(CustomBook, id=id)

    context = {'kbook': kbook,
               'group': group}
    
    if request.method == 'POST':
        if kbook.owner != request.user:
            if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = 'pending').exists():
                borrow = get_object_or_404(Borrow, custom_book = kbook, status = 'pending', borrower = request.user)
                borrow.status = 'on_going'
            else:
                borrow = Borrow(custom_book = kbook, status = 'on_going', borrower = request.user)
        else:
            borrower = request.POST.get('borrower')
            borrower = get_object_or_404(CustomUser, id=borrower)
            if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = 'pending').exists():
                borrow = get_object_or_404(Borrow, custom_book = kbook, status = 'pending', borrower = borrower)
                borrow.status = 'on_going'
                borrow.need_borrow_confirmation = True
                borrower.save()
            else:
                borrow = Borrow(custom_book = kbook, status = 'on_going', borrower = borrower, need_borrow_confirmation = True)
            messages.success(request, f'Please ask {borrower} to confirm the loan')

        borrow.save()
        kbook.is_disponible = False
        kbook.save()
        
        return redirect('book-detail', kbook.slug)


    return render(request, 'books/borrow/borrow-within-group.html', context=context)

@login_required
def borrow_book_no_group(request, id):
    kbook = get_object_or_404(CustomBook, id=id)
    groups = CustomGroup.objects.filter(members__id__contains = kbook.owner.id)
   
    common_members = []
    for group in groups:
        for member in group.members.all():
            if member != kbook.owner:
                common_members.append(member)
    common_members = set(common_members)

   


    context = {'kbook': kbook,
               'common_members': common_members,
               }
    
    if request.method == 'POST':
        if kbook.owner != request.user:
            if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = 'pending').exists():
                borrow = get_object_or_404(Borrow, custom_book = kbook, status = 'pending', borrower = request.user)
                borrow.status = 'on_going'
            else:
                borrow = Borrow(custom_book = kbook, status = 'on_going', borrower = request.user)
        else:
            kborrower = request.POST.get('kborrower')
            
            if kborrower == "None":
                print("pas")
                borrower = request.POST.get('borrower')
                borrower = get_object_or_404(CustomUser, id=borrower)
                if Borrow.objects.filter(custom_book = kbook, borrower = request.user, status = 'pending').exists():
                    borrow = get_object_or_404(Borrow, custom_book = kbook, status = 'pending', borrower = borrower)
                    borrow.status = 'on_going'
                    borrow.need_borrow_confirmation = True
                    borrower.save()
                else:
                    borrow = Borrow(custom_book = kbook, status = 'on_going', borrower = borrower, need_borrow_confirmation = True)
                messages.success(request, f'Please ask {borrower} to confirm the loan')

            else:
                borrower = kborrower
                borrow = Borrow(custom_book = kbook, status = 'on_going', custom_borrower=borrower)


            

        borrow.save()
        kbook.is_disponible = False
        kbook.save()
        
        return redirect('book-detail', kbook.slug)


    return render(request, 'books/borrow/borrow-within-group.html', context=context)

@login_required
def reserve_book_within_group(request, id, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    kbook = get_object_or_404(CustomBook, id=id)

    context = {'kbook': kbook,
               'group': group}
    
    if request.method == 'POST':
        reservation = Borrow(custom_book = kbook, status = 'pending', borrower = request.user)
        reservation.save()
        return redirect('book-detail', kbook.slug)


    return render(request, 'books/borrow/reserve-within-group.html', context=context)

@login_required
def reserve_book_no_group(request, id):
    
    kbook = get_object_or_404(CustomBook, id=id)

    context = {'kbook': kbook,
               }
    
    if request.method == 'POST':
        reservation = Borrow(custom_book = kbook, status = 'pending', borrower = request.user)
        reservation.save()
        return redirect('book-detail', kbook.slug)


    return render(request, 'books/borrow/reserve-within-group.html', context=context)

@login_required
def delete_reservation(request, id):
    kbook= get_object_or_404(CustomBook, id=id)
    borrow = Borrow.objects.filter(custom_book = kbook, status="pending", borrower=request.user)

    borrow.delete()

    messages.success(request, _("Reservation cancelled !"))

    
    return redirect('book-detail', kbook.slug)


@login_required
def give_back(request, id):
    borrow = get_object_or_404(Borrow, id=id)
    kbook = borrow.custom_book
    

    if request.method == 'POST':
        borrow.status="returned"
        if kbook.owner == request.user:
            borrow.borrow_end=timezone.now()
            borrow.need_return_confirmation = False
            kbook.is_disponible = True
            kbook.save()
        else:
            borrow.need_return_confirmation = True
            messages.success(request, f'Please ask {kbook.owner} to confirm the return')
    
        borrow.save()
        return redirect('book-detail', kbook.slug)
    
    return render(request, "books/borrow/borrow-within-group.html", {'borrow':borrow, 'kbook':kbook})

@login_required
def confirm_borrow(request, id):
    borrow = get_object_or_404(Borrow, id=id)
    kbook = borrow.custom_book

    if request.method == "POST":
        borrow.need_borrow_confirmation = False
        borrow.save()
        return redirect("book-detail", kbook.slug)  
    
    context = {
        'borrow':borrow,
        'kbook':kbook,
    }

    return render(request, 'books/borrow/borrow-within-group.html', context=context)     


