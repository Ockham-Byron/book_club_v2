from django.contrib.auth import get_user_model
from groups.models import CustomGroup

User = get_user_model

def get_groups(request):
    if request.user.is_authenticated:
        groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
        nb_of_groups = len(groups)
        if nb_of_groups == 0:
            groups = None
        elif nb_of_groups >= 1:
            groups = groups
            
        context = {'groups': groups}
        
    
    else:
        groups = None
        context = {'groups':groups}
    
    return context