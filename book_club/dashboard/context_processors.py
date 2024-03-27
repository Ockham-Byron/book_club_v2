from django.contrib.auth import get_user_model
from groups.models import CustomGroup

User = get_user_model

def get_groups(request):
    if request.user.is_authenticated:
        groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
        nb_of_groups = len(groups)
        library = CustomGroup.objects.get(leader=request.user, group_type="library")
        wishlist = CustomGroup.objects.get(leader=request.user, group_type="wishlist")
        if nb_of_groups <= 2:
            groups = None
        elif nb_of_groups >= 3:
            groups = groups
            
        context = {'groups': groups,
                   'library': library,
                   'wishlist': wishlist}
        
    
    else:
        groups = None
        context = {'groups':groups}
    
    return context