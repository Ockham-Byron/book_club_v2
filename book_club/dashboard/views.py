from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from groups.models import CustomGroup

User = get_user_model

def get_groups(user):
    groups = CustomGroup.objects.filter(members__id__contains=user.id)
    nb_of_groups = len(groups)
    if nb_of_groups == 0:
        group = None
    elif nb_of_groups >= 1:
        group = groups
        

    return group

# Create your views here.
def dashboard_view(request):
  print("Dashboard clicked!")
  if request.user.is_authenticated:
    print("is_authenticated")
    group = get_groups(request.user)
    if group is None: 
        print("rien")
        return redirect('all-groups')
    else:
        print("dashboard")
        
        context = {'user': request.user,
                   }
        return render(request, 'dashboard/dashboard.html', context=context)
   
  else:
    return redirect('login')