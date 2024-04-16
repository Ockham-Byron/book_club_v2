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
from .models import Book, Meeting, CustomBook, Comment

tz= timezone.get_current_timezone()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

# Create your views here.
def book_search(search):
    api = "https://www.googleapis.com/books/v1/volumes?q=search:"
  
    search = search
    
    if (search == False) or (search == ""):
            return redirect('book-search')

    search = search.replace(' ', '+')
    r = urlopen(api + search, context=ctx)
    
    data = json.load(r)
    
    
    fetched_books = data['items']
    books = []
    for book in fetched_books:
        book_dict = {
            'title': book['volumeInfo']['title'],
            'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "static/assets/img/illustrations/book-placeholder.jpeg",
            'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
            'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
            'info': book['volumeInfo']['infoLink'],
            'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0,
            'isbn': book['volumeInfo']['industryIdentifiers'][0]['identifier'] if 'industryIdentifiers' in book['volumeInfo'] else 0,
        }
        books.append(book_dict)

    return books

def book_save(id):
    api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
  
    isbn = id
  
    r = urlopen(api + isbn, context=ctx)
    print(r)
    book_data = json.load(r)
  # if r.status_code != 200:
  #     return render(request, 'books/book-results.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

  # data = r.json()

    volume_info = book_data["items"][0]["volumeInfo"]

  
    book={}
 
    book = {
        'title': volume_info['title'],
        'cover': volume_info['imageLinks']['thumbnail'] if 'imageLinks' in volume_info else "static/assets/img/illustrations/book-placeholder.jpeg",
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


@login_required
def add_book(request, id):
    book_in_db = None
    kgroups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    
    book=book_save(id)
   
    
    context = {
        'kgroups':kgroups,
        'book':book,
    }

    if Book.objects.filter(isbn=id).exists():
        book_in_db = Book.objects.get(isbn=id)
    
    print(book_in_db)


    if request.method=='POST':
        groups = request.POST.getlist('group')
        print(groups)
        if len(groups) == 0:
            print('No groups')
            messages.error(request, _('You have to choose where to register this book.'))
        else:
            if book_in_db:
                for i in groups:
                    group = CustomGroup.objects.get(uuid=i)
                    book_in_db.groups.add(group)
                    new_kbook = CustomBook(book=book_in_db, group=group)
                    if group.group_type == 'library':
                        new_kbook.owner = request.user
                        new_kbook.save()
                    elif group.group_type == 'several_books':
                        new_kbook.owner = request.user
                        new_kbook.save()
                    else:
                        new_kbook.admin = request.user
                        new_kbook.save()
                book_in_db.save()
                

            else:
                new_book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
                new_book_in_db.save()
                
                for group in groups:
                    new_book_in_db.groups.add(group)
                    group = CustomGroup(uuid=group)
                    new_kbook = CustomBook(book=new_book_in_db, group=group)
                    if group.group_type == 'library' or group.group_type == 'several_books':
                        new_kbook.owner = request.user
                        new_kbook.admin = request.user
                        new_kbook.save()
                    else:
                        new_kbook.admin = request.user
                        new_kbook.save()
                new_book_in_db.save()
                return redirect('all-books')

            return redirect('all-books')
    
    return render(request, 'books/book-search-detail.html', context)

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
                books = book_search(search)
                return render(request, 'books/search.html', {'form': form, 'books': books})
            except:
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
    book=book_save(isbn)
    
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
    book=book_save(isbn)
    
    context = {
        'meeting': meeting,
        'book':book,
    }

    if Book.objects.filter(isbn=isbn).exists():
        book_in_db = Book.objects.get(isbn=isbn)

    if request.method=='POST':
        if book_in_db:
            book_in_db.groups.add(group)
            book_in_db.save()
            new_kbook = CustomBook(book=book_in_db, group=group, admin=request.user)
            new_kbook.save()
            meeting.book=new_kbook
           

        else:
            
            new_book_in_db = Book(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'), description=book.get('description'), pages=book.get('pages'))
            new_book_in_db.save()
            new_book_in_db.groups.add(group)
            new_book_in_db.save()
            new_kbook = CustomBook(book=new_book_in_db, group=group, admin=request.user)
            new_kbook.save()
            meeting.book = new_kbook
        meeting.save()
        return redirect('group-detail', group.slug)
    
    return render(request, 'books/book-search-detail.html', context)
@login_required
def book_detail(request, slug):
    user = request.user
    groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    groups = groups.exclude(group_type="library")
    groups = groups.exclude(group_type="wishlist")
    kbook = get_object_or_404(CustomBook, slug=slug)
    book = kbook.book
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



    all_reviews = Comment.objects.filter(book=book)
    #filter by groups
    
    author_filter = Q()
    for group in groups:
        author_filter |= Q(author__group_members = group)

    group_reviews = all_reviews.filter(author_filter).distinct()
    print(group_reviews)
    

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
     
     books = Book.objects.filter(groups__in=user_groups).distinct()
     kbooks= CustomBook.objects.filter(book__in=books)

     unique_kbooks = set(kbook.isbn for kbook in kbooks) 
     print(unique_kbooks)

     #gérer les doublons
     list_isbn=[kbook.isbn for kbook in kbooks]
     isbn_counts = {}
     for isbn in list_isbn:
        if isbn in isbn_counts:
            isbn_counts[isbn] += 1
        else:
            isbn_counts[isbn] = 1
    
     duplicate_isbns = [isbn for isbn, count in isbn_counts.items() if count > 1]

     duplicate_kbooks = kbooks.filter(isbn__in=duplicate_isbns)

     if duplicate_kbooks.filter(owner = request.user).exists():
        for kbook in duplicate_kbooks:
            if kbook.owner != request.user:
                kbooks = kbooks.exclude(id=kbook.id)
        
     elif duplicate_kbooks.filter(admin = request.user).exists():
         for kbook in duplicate_kbooks:
            if kbook.admin != request.user:
                kbooks = kbooks.exclude(id=kbook.id)

     if duplicate_kbooks.filter(owner = request.user, group__group_type__contains = "several").exists():
         print("ça existe")
         for kbook in duplicate_kbooks:
             if kbook.group != None:
                if kbook.owner == request.user and kbook.group.group_type == "several_books":
                    kbooks = kbooks.exclude(id=kbook.id)
    

     context = {
         'books': books,
         'kbooks': kbooks,
     }
     return render(request, 'books/all-books.html', context)

@login_required
def group_books(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    kbooks = CustomBook.objects.filter(group=group)

    context = {'kbooks': kbooks,
               'group': group}
    
    return render(request, 'books/all-books.html', context)

@login_required
def delete_book(request, slug):
    kbook = CustomBook.objects.get(slug=slug)
    if kbook.picture:
        os.remove(kbook.picture.path)
        kbook.picture.delete()
    kbook.delete()
    return redirect('all-books')
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

    return render(request, "books/add-comment.html", {'form':form, 'book':book})


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

def delete_meeting(request, id):
    pass


