import json
import environ
import ssl
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from urllib.request import urlopen
from django.shortcuts import render, redirect
from .forms import BookSearch, AddMeetingForm
from groups.models import CustomGroup
from .models import Book, Meeting

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
    groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    
    users = []
    for group in groups:
        users.extend(group.members.all())
    

    book=book_save(id)
   
    
    context = {
        'groups':groups,
        'users':users,
        'book':book,
    }

    if request.method=='POST':
        print("POST request")
        groups = request.POST.getlist('group')
        new_book = Book.objects.create(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'))
        for group in groups:
            new_book.groups.add(group)
        new_book.save()
        return redirect('dashboard')
    
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
            books = book_search(search)
            return render(request, 'books/search.html', {'form': form, 'books': books})
        
@login_required
def add_meeting(request, slug):
    group = CustomGroup.objects.get(slug=slug)
    books = Book.objects.filter(groups__id__contains = group.id)
    form = AddMeetingForm()

    if request.method == 'POST':
        form = AddMeetingForm(request.POST)
        meeting_at = request.POST.get('meeting_at')
        if form.is_valid():
            if "search-book" in request.POST:
                meeting = form.save()
                meeting.meeting_at = meeting_at
                meeting.group = group
                meeting.save()
                return redirect('search-book-for-meeting', meeting.id)
        else:
            print(form.errors)

    context = {'form': form,
               'group': group,
                'books':books, }
    
    return render(request, "books/meetings/add-meeting.html", context=context)





def edit_meeting(request, uuid):
    pass

def delete_meeting(request, uuid):
    pass

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
def add_new_book_to_meeting(request,id, isbn):
    meeting = Meeting.objects.get(id=id)
    group = meeting.group
    book=book_save(isbn)
    
    context = {
        'meeting': meeting,
        'book':book,
    }

    if request.method=='POST':
        new_book = Book.objects.create(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'), isbn=book.get('isbn'))
        new_book.groups.add(group)
        new_book.save()
        meeting.book = new_book
        meeting.save()
        return redirect('group-detail', group.slug)
    
    return render(request, 'books/book-search-detail.html', context)