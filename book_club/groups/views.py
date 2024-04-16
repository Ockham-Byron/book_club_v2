import uuid
from django.shortcuts import render, redirect
from django.utils.timezone import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.utils.text import slugify
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
            messages.add_message(request, messages.SUCCESS ,message= _(f'New group {group.kname} created successfully'), extra_tags=_('Great !'))
            return redirect('all-groups')

    return render(request, 'groups/add_group.html', {'form': form,})

@login_required
def add_library_view(request):
    if CustomGroup.objects.filter(leader=request.user, group_type="library").exists():
        library=CustomGroup.objects.get(leader=request.user, group_type="library")
        return redirect('library', library.slug)
    library_uuid=uuid.uuid4()
    name='My_Library_' + str(library_uuid)
    slug=slugify(name) 
    library = CustomGroup(uuid=library_uuid, name=name, slug=slug, kname=_('My Library'), leader=request.user, group_type='library')
    library.members.add(request.user)
    library.save()
    
    

    return redirect('library', library.slug)

@login_required
def add_wishlist_view(request):
    if CustomGroup.objects.filter(leader=request.user, group_type="wishlist").exists():
        wishlist=CustomGroup.objects.get(leader=request.user, group_type="wishlist")
        return redirect('wishlist', wishlist.slug)
    wishlist_uuid=uuid.uuid4()
    name='My_Wishlist_' + str(wishlist_uuid)
    slug=slugify(name) 
    wishlist = CustomGroup.objects.create(uuid=wishlist_uuid, name=name, slug=slug, kname=_('My Wishlist'), leader=request.user, group_type='wishlist')
    
    wishlist.members.add(request.user)
    wishlist.save()

    return redirect('wishlist', wishlist.slug)


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
    return render(request, 'groups/member_groups.html')


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = CustomGroup
    template_name = 'groups/group_detail.html'
    slug_url_kwarg = 'slug'
    
    

    

    def get_context_data(self, **kwargs):
        group = self.object
        next_meeting = group.meeting_set.filter(meeting_at__gte=datetime.now()).first()
        nb_of_readers = 0
        if next_meeting:
            next_book = next_meeting.book
            if next_book:
                nb_of_readers = next_book.book.readers.filter(group_members = group).count()
        context = super().get_context_data(**kwargs)
        context['members'] = group.members.all()
        context['nb_of_users'] = group.members.all().count()
        context['nb_of_books'] = group.kbook_group.all().count() 
        context['books'] = group.kbook_group.all().order_by('-created_at')[:10]
        context['next_meeting'] = next_meeting
        context['nb_of_readers'] = nb_of_readers

        return context
    
class LibraryView(LoginRequiredMixin, DetailView):
    model = CustomGroup
    template_name = 'groups/library.html'
    slug_url_kwarg = 'slug'
    

    

    def get_context_data(self, **kwargs):
        group = self.object
        
        context = super().get_context_data(**kwargs)
        context['nb_of_books'] = group.kbook_group.all().count() 
        context['books'] = group.kbook_group.all()

        return context
    

class WishlistView(LoginRequiredMixin, DetailView):
    model = CustomGroup
    template_name = 'groups/library.html'
    slug_url_kwarg = 'slug'
    

    

    def get_context_data(self, **kwargs):
        group = self.object
        
        context = super().get_context_data(**kwargs)
        
        context['nb_of_books'] = group.kbook_group.all().count() 
        context['books'] = group.kbook_group.all()
        

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
