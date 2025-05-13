from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from groups.models import CustomGroup

User = get_user_model

def get_groups(user):
    groups = CustomGroup.objects.filter(members__id__contains=user.id)
    nb_of_groups = len(groups)
    if nb_of_groups <= 2:
        group = None
    elif nb_of_groups >= 3:
        group = groups
        

    return group

# Create your views here.
def dashboard_view(request):
  if request.user.is_authenticated:
    group = get_groups(request.user)
    print(group)
    
    if group is None: 
        return redirect('all-groups')
    else:
        return render(request, 'dashboard/dashboard.html')
   
  else:
    return redirect('login')
  
def install_app_view(request):
    return render(request, 'dashboard/install-app.html')