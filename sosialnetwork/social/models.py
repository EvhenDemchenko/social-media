from tkinter import CASCADE
from django.db import models
from django.templatetags.tz import TimezoneNode
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Image(models.Model):
    image = models.ImageField(upload_to='uploads/post_pictures'  ,blank=True, null=True)    
    
class Post(models.Model) :
    shared_body = models.TextField(blank=True, null=True)
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    shared_on = models.DateTimeField(default=timezone.now)

    body = models.TextField()
    image = models.ManyToManyField(Image, blank=True) 
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')

    class Meta:
        ordering = ['-created_on', '-shared_on']


class Comment(models.Model):
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User , blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User , blank=True, related_name='comment_dislikes')

    parent = models.ForeignKey('self', on_delete=models.CASCADE , related_name='replies' , null=True, blank=True)

    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('-created_on')
    def is_parent(self):
        return self.parent is None

 
     

class UserProfile(models.Model):
    username=models.CharField(max_length=30, null=True, blank=True)
    name = models.CharField(max_length=30 , null=True , blank=True )
    bio = models.TextField(max_length=500 , null=True , blank=True) 
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=30 , null=True , blank=True )
    picture = models.ImageField(upload_to='uploads/profile_pictures' , default='uploads/profile_pictures/baseavatar.jpg' ,blank=True, null=True)
    
    user = models.OneToOneField(User , on_delete=models.CASCADE, primary_key=True, related_name='profile' , verbose_name='user')
    followers = models.ManyToManyField(User , blank=True, related_name='followers')

# signals for userprofile 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, username=instance.username )

    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Notification(models.Model):
    # 1 = like 2 = comment 3 = follow 4 = DM
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name = 'notification_to', null=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_from' ,null=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    thread = models.ForeignKey('ThreadModel', on_delete=models.CASCADE, blank=True, null=True)

    user_has_seen = models.BooleanField(default=False)


class ThreadModel(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User , on_delete=models.CASCADE, related_name='+')

class MessageModel(models.Model):
    thread = models.ForeignKey(ThreadModel, on_delete=models.CASCADE, related_name='+' , blank=True, null=True )
    sender_user = models.ForeignKey(User , on_delete=models.CASCADE,related_name="+",  )
    receiver_user = models.ForeignKey(User , on_delete=models.CASCADE,related_name="+",  )
    body = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='pictures/message_photos' , blank=True , null=True)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

