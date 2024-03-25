import requests
import json
import environ
import ssl
from urllib.request import urlopen
from django.shortcuts import render, redirect
from .forms import BookSearch
from .models import Result

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

# Create your views here.
def book_search(request):
  form = BookSearch()
  return render(request, 'books/book-search.html', {'form': form})

def book_results(request):
  api = "https://www.googleapis.com/books/v1/volumes?q=search:"
  
  search = request.GET.get('search', False)
  

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
          'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "",
          'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
          'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
          'info': book['volumeInfo']['infoLink'],
          'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0
      }
      books.append(book_dict)

  def sort_by_pop(e):
      return e['popularity']

  books.sort(reverse=True, key=sort_by_pop)

  return render(request, 'books/book-results.html', {'books': books})

def search(request):
    if request.method == 'GET':
        form = BookSearch()
        return render(request, 'books/search.html', {'form': form})
    else:
        form = BookSearch(request.POST)
        if form.is_valid():
            term = form.cleaned_data['search']
            result = Result(title=term)
            result.save()
            results = Result.objects.all()
            return render(request, 'books/search.html', {'form': form, 'results': results})