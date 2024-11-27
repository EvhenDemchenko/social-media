from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Image,  Notification, Post , Comment, ThreadModel , UserProfile, MessageModel
from .forms import  CommentForm, MessageForm, PostForm, ProfileForm, ThreadForm , ShareForm
from django.views.generic.edit import CreateView ,UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



#POST VIEW
class PostListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    form_class = PostForm
    share_form_class = ShareForm
    context_object_name = 'posts'
    template_name = 'social/post_list.html'

    def get_queryset(self) :
        return Post.objects.all().order_by('-created_on')

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create post'
        context['form'] = self.form_class()
        context['shareform'] = self.share_form_class
        return context

class PostListViewFollowing(LoginRequiredMixin, ListView):
    paginate_by = 3

    form_class = PostForm 
    context_object_name = 'posts'
    template_name = 'social/post_list.html'

    def get_queryset(self):
        user = self.request.user
        posts = Post.objects.filter(
            Q(author__profile__followers=user)
        ).order_by('-created_on')
        return posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Following posts'
        context['form'] = self.form_class()
        return context
     
    def post(self, request, *args, **kwargs) :
        form = self.form_class(request.POST)
        if form.is_valid() :
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
        return super().get(request, *args, **kwargs)

class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_list.html'

    def form_valid(self, form):
        files = self.request.FILES.getlist("image") 
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        for f in files:
            img = Image(image=f)
            img.save()
            post.image.add(img)  
        messages.success(self.request, 'success')
        return super().form_valid(form)
        # except:
        #     messages.success(self.request, 'not success')
        #     return redirect('social:post-list')
    

    def get_success_url(self) -> str:
        return reverse_lazy('social:post-list')

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'social/post_detail.html'
    # form_class = CommentForm

    def get_object(self, queryset=None):
        current_post = Post.objects.get(pk=self.kwargs['pk'])
        return current_post 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['form'] = self.form_class if want to user form_class on page should return self.form_class
        context['title'] = 'Post detail'
        context['comments'] = Comment.objects.filter(post=self.object)
        context['post'] = self.get_object()
        return context
    
class PostEditView(LoginRequiredMixin, UserPassesTestMixin , UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'social/post_edit.html'

    def form_valid(self, form):
        files = self.request.FILES.getlist("image") 
        post = form.save(commit=False)
        post.author = self.request.user
        # remove all images many to many field
        post.image.clear()
        # remove all images many to many field
        post.save()
        for f in files:
            img = Image(image=f)
            img.save()
            post.image.add(img)  
        messages.success(self.request, 'success')
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('social:post-detail', kwargs={'pk': self.kwargs['pk']})
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('social:post-list')
    template_name = 'social/post_delete.html'
    

    def get_objects(self,queryset=False):
        current_post = Post.objects.get(pk = self.kwargs['pk'])
        return current_post

                
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if isinstance(self.get_object(), Post):
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        return redirect('social:post-list')
       
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

#COMMENT  VIEW
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk,  *args, **kwargs):
        content = request.POST.get('comment')
        post = Post.objects.get(pk=pk)
        comment = Comment.objects.create(comment=content, author=request.user, post=post)

        if request.user != comment.author:
            notification = Notification.objects.create(notification_type = 2, to_user=post.author , from_user=request.user , comment=comment,)


        comment.save()
        return HttpResponseRedirect(reverse_lazy('social:post-detail' , kwargs={"pk":pk}))
           
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
        model = Comment
        template_name = 'social/comment_delete.html'

        def get_success_url(self) -> str:
            pk = self.kwargs['pk']
            return reverse_lazy('social:post-detail', kwargs={'pk':pk})

        def get_object(self, queryset=None):
            post_pk = self.kwargs['pk']
            comment_pk = self.kwargs['comment_pk']
            author = self.request.user
            current_comment = Comment.objects.get(pk=comment_pk, post=post_pk, author=author)       
            return current_comment
        
        def post(self, request, *args, **kwargs):
            self.object = self.get_object()
            if isinstance(self.get_object(), Comment):
                self.object.delete()
                return HttpResponseRedirect(self.get_success_url())
            return redirect('social:post-detail', pk=self.kwargs['pk'])
        
        def test_func(self):
            comment = self.get_object()
            return self.request.user == comment.author

class CommentReplyView(LoginRequiredMixin, View):

    def post(self, request , pk , comment_pk , *args, **kwargs):

        form = CommentForm(request.POST)
        post = Post.objects.get(pk=pk)
        parent_comment = Comment.objects.get(pk=comment_pk)



        if form.is_valid():    
            reply_comment = form.save(commit=False)

            reply_comment.author = request.user
            reply_comment.post = post
            reply_comment.parent = parent_comment

            reply_comment.save()
        if request.user != parent_comment.author:
            notification = Notification.objects.create(notification_type = 2, to_user= parent_comment.author , from_user=request.user , comment=parent_comment,)

        return HttpResponseRedirect(reverse_lazy('social:post-detail' , kwargs={"pk":pk}))
    
#PROFILE VIEW
class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    context_object_name = 'profile'
    template_name = 'social/profile_detail.html'

    def get_object(self, queryset = False):
        pk = self.kwargs['pk']
    
        return UserProfile.objects.get(pk=pk)
    
    def get_context_data(self, **kwargs):
        profile_user = self.get_object()

        followers = profile_user.followers.all()
        number_of_followers = len(followers)
        subscript = UserProfile.objects.filter(followers = profile_user.user)

        context = super().get_context_data(**kwargs)
        context['title'] = 'User Profile'
        context['posts'] =  Post.objects.filter(author=profile_user.user)
        context['subscript'] = subscript
        context['number_of_followers'] = number_of_followers

        return context

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin ,UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name= 'social/profile_edit.html'

    def get_success_url(self):
        return reverse_lazy('social:profile-detail', kwargs={'pk': self.kwargs['pk']})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user
    
    def handle_no_permission(self):
        return redirect('social:post-list')

#FOLLOWER  & SUBS
class AddFollower(LoginRequiredMixin,View):
    def post(self, request,pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        if request.user != profile.user:
            notification = Notification.objects.create(notification_type = 3, to_user=profile.user , from_user=request.user )


        return redirect('social:profile-detail', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk , *args , **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('social:profile-detail', pk=profile.pk)

class ListOfFollowers(LoginRequiredMixin, ListView):
    model = UserProfile
    context_object_name = 'followers'
    template_name = 'social/follower_list.html'
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        user_profile_followers = UserProfile.objects.get(pk=pk).followers.all()
        return user_profile_followers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Followers'
        return context
    
class ListOfSubscription(LoginRequiredMixin,ListView):
    model = UserProfile
    context_object_name = 'subscription'
    template_name = 'social/subscription_list.html'

    def get_queryset(self):
        pk = self.kwargs['pk']
        current_profile = UserProfile.objects.get(pk=pk)
        subscript = UserProfile.objects.filter(followers = current_profile.user)
        return subscript
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['title']= 'Subs'
        return context

#LIKE AND DISLIKE
class LikePost(LoginRequiredMixin , View):
    def post(self, request , pk , *args, **kwargs):
        user = request.user
        post = Post.objects.get(pk=pk)
        likes = post.likes.all()
        dislikes = post.dislikes.all()

        if user in dislikes:
            post.dislikes.remove(user)

        if user in likes:
            post.likes.remove(user)

        else :
            post.likes.add(user)
            if request.user != post.author:
                notification = Notification.objects.create(notification_type = 1, to_user=post.author , from_user=request.user , post=post,)

        return redirect('social:post-detail', pk=pk)

class DislikePost(LoginRequiredMixin , View):
    def post(self,request,pk, *args, **kwargs):
        user = request.user
        post = Post.objects.get(pk=pk)
        dislikes = post.dislikes.all()
        likes = post.likes.all()

        if user in likes:
            post.likes.remove(user)

        if user in dislikes:
            post.dislikes.remove(user)
        else:
            post.dislikes.add(user)


        return redirect('social:post-detail', pk=pk)

class CommentLikeView(LoginRequiredMixin, View):
    def post(self, request, comment_pk, pk, *args, **kwargs):
        user = request.user
        comment = Comment.objects.get(pk=comment_pk)

        if user in comment.dislikes.all():
            comment.dislikes.remove(user)

        if user in comment.likes.all():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)
            notification = Notification.objects.create(notification_type = 1, to_user=comment.author , from_user=request.user , comment=comment,)


        return redirect('social:post-detail', pk=pk)

class CommentDislikeView(LoginRequiredMixin, View):
    def post(self, request, comment_pk ,pk , *args, **kwargs):
        user = request.user 
        comment = Comment.objects.get(pk=comment_pk)
        
        if user in comment.likes.all():
            comment.likes.remove(user)

        if user in comment.dislikes.all():
            comment.dislikes.remove(user)
        else:
            comment.dislikes.add(user)

        return redirect('social:post-detail', pk=pk)
    
#SEARCH USER
class SearchProfile(View):
    def get(self,request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)

        )
    
        context = {
            "profile_list":profile_list
        }

        return render(request , 'social/profile_search.html', context)

#NOTIFICATIONS 
class PostNotifications(View):
    def get(self, request, notification_pk ,post_pk,  *args, **kwargs):
        notifications = Notification.objects.get(pk=notification_pk)


        notifications.user_has_seen = True
        notifications.save()

        return redirect('social:post-detail', pk=post_pk)

class FollowNotification(View):
    def get(self, request,notification_pk , *args, **kwargs):
        notification = Notification.objects.get(pk = notification_pk)
        profile_pk = notification.from_user.pk

        notification.user_has_seen = True
        notification.save()

        return redirect('social:profile-detail' , pk = profile_pk )

class RemoveNotification(View):
    def get(self, request, notification_pk , *args, **kwargs):  
        notification = Notification.objects.get(pk = notification_pk)
        notification.delete()
        return redirect(request.META.get('HTTP_REFERER', '/'))

class ListThreads(ListView):
    model = ThreadModel
    template_name = 'social/inbox.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return ThreadModel.objects.filter(Q(user=self.request.user) | Q(receiver=self.request.user))

class CreateThread(View):
    def get(self, request , *args , **kwargs):
        form = ThreadForm()

        context = {
            'form':form
        }

        return render(request, 'social/create_thread.html', context)
    def post(self , request , *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user = request.user , receiver = receiver).exists():
                thread = ThreadModel.objects.filter(user = request.user , receiver = receiver) 
                return redirect('social:thread' , pk=thread.pk)
            elif ThreadModel.objects.filter(user = receiver, receiver = request.user).exists():
                thread = ThreadModel.objects.filter(user = receiver , receiver = request.user)
                return redirect('social:thread' , pk=thread.pk)
            
            if form.is_valid():
                thread = ThreadModel(
                    user = request.user ,
                    receiver = receiver
                )

                thread.save()
                return redirect('social:thread' , pk=thread.pk)
        except:

            messages.error(request, 'invalid username')
            return redirect("social:create-thread")
   
class ThreadView(View):
    def get (self, request ,pk, *args, **kwargs):
        form = MessageForm
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains = pk)

        context = {
            'thread':thread,
            'message_list':message_list,
            'form':form
        }
        notification = Notification.objects.filter(thread__pk__contains = pk)
        if notification.exists() and notification[0].from_user == request.user:
            notification.update(user_has_seen = True)

        return render(request, 'social/thread.html', context)

class CreateMessage(CreateView):
    model = MessageModel
    form_class = MessageForm
    template_name = 'social/thread.html'

    def form_valid(self, form):
        thread = ThreadModel.objects.get(pk=self.kwargs['pk'])
        
        if thread.receiver == self.request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        
        message = form.save(commit=False)
        message.thread = thread
        message.sender_user = self.request.user
        message.receiver_user = receiver
        message.save()


        notification = Notification.objects.create(
            notification_type = 4, 
            from_user = self.request.user,
            to_user = receiver,
            thread = thread 
        )
        return super().form_valid(form) 
    
    def get_success_url(self):
        return reverse_lazy('social:thread', kwargs={'pk':self.kwargs['pk']})




# class ShareFormView(View):
#     def post(self,request, pk ,*args , **kwargs):
#         original_post = Post.objects.get(pk=pk)
#         form = ShareForm(request.POST)

#         if form.is_valid():
#             new_post = Post(
#                 shared_body = self.request.POST.get('body'),
#                 body = original_post.body,
#                 author = original_post.author,
#                 created_on = original_post.created_on,
#                 shared_user = request.user,
#                 shared_on = timezone.now()
#             )
#             new_post.save()

#             for file in original_post.image.all():
#                 new.post.image.add(file)

#             new_post.save()

#         return redirect('social:post-list')



# class FormThreadView(View):
#     def get(self, request, *args, **kwargs):
#         form = ThreadForm()
#         context = {
#             'form': form
#         }
#         return render(request, 'social/create_thread.html', context)
# class CreateThreadView(CreateView):
#     form_class = ThreadForm
#     template_name = 'social/create_thread.html'

#     def form_valid(self, form):
#         username = form.cleaned_data.get('username')
#         receiver = User.objects.get(username=username)

#         if ThreadModel.objects.filter(user = self.request.user , receiver = receiver).exists():
#             thread = ThreadModel.objects.filter(user = self.request.user , receiver = receiver) 
#             return redirect('social:thread' , pk=thread.pk)
#         elif ThreadModel.objects.filter(user = receiver, receiver = self.request.user).exists():
#             thread = ThreadModel.objects.filter(user = receiver , receiver = self.request.user)
#             return redirect('social:thread' , pk=thread.pk)

#         thread = ThreadModel(
#             user = self.request.user ,
#             receiver = receiver
#         )

#         thread.save()
#         return redirect('social:thread' , pk=thread.pk)





