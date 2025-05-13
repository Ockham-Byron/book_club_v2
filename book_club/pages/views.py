from django.shortcuts import render

# Create your views here.
def bye_page(request):
  return render(request,'pages/bye.html')

def page_not_found_view(request, exception):
  return render(request,'pages/page_not_found.html', status=404)