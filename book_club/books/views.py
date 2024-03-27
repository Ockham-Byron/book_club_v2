import json
import environ
import ssl
from django.utils.translation import gettext_lazy as _
from urllib.request import urlopen
from django.shortcuts import render, redirect
from .forms import BookSearch
from groups.models import CustomGroup
from users.models import CustomUser
from .models import Book


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

# Create your views here.

def book_search_detail(request, id):
    groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    
    users = []
    for group in groups:
        users.extend(group.members.all())
    

    
   
    
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
        'isbn': volume_info['industryIdentifiers'][0]['identifier']
        # 'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
        # 'info': book['volumeInfo']['infoLink'],
        # 'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0
    }
      
    context = {
        'groups':groups,
        'users':users,
        'book':book,
    }

    if request.method=='POST':
        print("POST request")
        groups = request.POST.getlist('group')
        
        


        

        new_book = Book.objects.create(title=book.get('title'), author=book.get('authors'), cover=book.get('cover'))
        for group in groups:
            new_book.groups.add(group)
        new_book.save()
        
        return redirect('dashboard')
    
    

    return render(request, 'books/book-search-detail.html', context)

def new_book_search(request):
    if request.method == 'GET':
        form = BookSearch()
        return render(request, 'books/search.html', {'form': form})
    else:
        form = BookSearch(request.POST)
        if form.is_valid():
            api = "https://www.googleapis.com/books/v1/volumes?q=search:"
  
            search = request.POST.get('search', False)
            

            if (search == False) or (search == ""):
                    return redirect('book-search')

            search = search.replace(' ', '+')
            print(search)
            r = urlopen(api + search, context=ctx)
            print(r)
            data = json.load(r)
            # if r.status_code != 200:
            #     return render(request, 'books/book-results.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

            # data = r.json()

            if not 'items' in data:
                return render(request, 'books/book-results.html', {'message': 'Sorry, no books match that search term.'})

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
                    'isbn': book['volumeInfo']['industryIdentifiers'][0]['identifier']
                }
                books.append(book_dict)
            # term = form.cleaned_data['search']
            # result = Result(title=term)
            # result.save()
            # results = Result.objects.all()
            return render(request, 'books/search.html', {'form': form, 'books': books})