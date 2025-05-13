# Python's built-in module for encoding and decoding JSON data
import json
import ssl
# Python's built-in module for opening and reading URLs
from urllib.request import urlopen



while True:
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE

    
  api = "https://www.googleapis.com/books/v1/volumes?q=search:&langRestrict='fr'"
  isbn = input("Enter 10 digit ISBN: ").strip()
  isbn = isbn.replace(" ", "+")

  # send a request and get a JSON response
  resp = urlopen(api + isbn, context=ctx)
  # parse JSON into Python as a dictionary
  book_data = json.load(resp)

  # create additional variables for easy querying
  volume_info = book_data["items"][0]["volumeInfo"]
  author = volume_info["authors"]
  # practice with conditional expressions!
  prettify_author = author if len(author) > 1 else author[0]

  # display title, author, page count, publication date
  # fstrings require Python 3.6 or higher
  # \n adds a new line for easier reading
  print(f"\nTitle: {volume_info['title']}")
  print(f"Author: {prettify_author}")
  print(f"Page Count: {volume_info['pageCount']}")
  print(f"Publication Date: {volume_info['publishedDate']}")
  print("\n***\n")

  # ask user if they would like to enter another isbn
  user_update = input("Would you like to enter another ISBN? y or n ").lower().strip()

  if user_update != "y":
    print("May the Zen of Python be with you. Have a nice day!")
    break # as the name suggests, the break statement breaks out of the while loop