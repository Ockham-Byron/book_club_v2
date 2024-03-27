import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from .forms import *
from .models import CustomGroup


@login_required
def add_group_view(request):
    form = AddGroupForm()
    
    user= request.user
    if request.method == 'POST':
        form = AddGroupForm(request.POST, request.FILES)
        group_pic = request.FILES.get('group_pic')
        
        if form.is_valid():
            group_type = request.POST.get('type')
            form.instance.leader = user
            group = form.save()
            group.group_pic = group_pic
            group.group_type = group_type
            group.members.add(user)
            group.save()
            group_name = group.name
            messages.add_message(request, messages.SUCCESS ,message= _(f'New group {group_name} created successfully'), extra_tags=_('Great !'))
            return redirect('all-groups')

    return render(request, 'groups/add_group.html', {'form': form,})

@login_required
def join_group_view(request):
    user = request.user
    if request.method == 'POST':
        group_code = request.POST.get('uuid')

        def is_valid_uuid(value):
            try:
                uuid.UUID(str(value))
                return True
            except ValueError:
                return False
        
        def group_exists(value):
            try:
                CustomGroup.objects.get(uuid=value)
                return True
            except CustomGroup.DoesNotExist:
                return False

        if is_valid_uuid(group_code):
            if group_exists(group_code):
                group = CustomGroup.objects.get(uuid=group_code)
                if user in group.members.all():
                    messages.error(request, f'Vous faites partie de ce groupe')
                else:
                    group.members.add(user)    
                    group.save()
                    return redirect('all-groups')
            
            else:
                messages.error(request, f'Ce groupe non')
                

        else:
            messages.error(request, f'Invalide')
            

    return render(request, 'groups/join_group.html')

@login_required
def all_groups(request):
    groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
    groups = groups.exclude(group_type="library")
    groups = groups.exclude(group_type="wishlist")
    context = {
        'groups': groups,
        
        }
    return render(request, 'groups/member_groups.html', context)


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = CustomGroup
    template_name = 'groups/group_detail.html'
    slug_url_kwarg = 'slug'
    

    

    def get_context_data(self, **kwargs):
        group = self.object
        
        context = super().get_context_data(**kwargs)
        context['members'] = group.members.all()
        context['nb_of_users'] = group.members.all().filter(is_guest=False).count()
        context['nb_of_books'] = group.books.all().count() 
        return context
    


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UpdateGroupForm
    model = CustomGroup
    
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'uuid'
    template_name = 'groups/update_group.html'

    def get_form_kwargs(self):
        kwargs = super(GroupUpdateView, self).get_form_kwargs()
        kwargs['group'] = CustomGroup.objects.get(uuid=self.object.uuid)
        return kwargs
