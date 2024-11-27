from django.urls import path
from .views import CreateThread, ListThreads, PostListView, PostDetailView, CommentCreateView, PostEditView, CreatePostView, PostDeleteView, CommentDeleteView, PostListViewFollowing , ProfileView, ProfileEditView, AddFollower, RemoveFollower, LikePost, DislikePost, SearchProfile, ListOfFollowers ,ListOfSubscription, CommentLikeView,CommentDislikeView, CommentReplyView, PostNotifications, FollowNotification, RemoveNotification , ThreadView, CreateMessage


app_name ='social'
 
urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('following', PostListViewFollowing.as_view(), name='post-list-following'),
    #post
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/create-post/', CreatePostView.as_view(), name='create-post'),
    path('post/<int:pk>/post-edit/', PostEditView.as_view(), name='post-edit'),
    path('post/<int:pk>/post-delete/', PostDeleteView.as_view(), name='post-delete'),
    #comment
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('post/<int:pk>/comment-reply/<int:comment_pk>/', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:pk>/comment-delete/<int:comment_pk>', CommentDeleteView.as_view(), name='comment-delete'),
    #profile
    path('profile/<int:pk>/profile-detail', ProfileView.as_view(), name='profile-detail' ),
    path('profile/<int:pk>/profile-edit', ProfileEditView.as_view(), name='profile-edit'),
    #follower
    path('profile/<int:pk>/follower-add', AddFollower.as_view(), name='follower-add' ),
    path('profile/<int:pk>/follower-remove', RemoveFollower.as_view(), name='follower-remove' ),
    path('profile/<int:pk>/followers/', ListOfFollowers.as_view(), name='followers'),
    #subscript profiles
    path('profile/<int:pk>/subscript/', ListOfSubscription.as_view(), name='subscript'),
    #likes & dislikes
    path('post/<int:pk>/post-like', LikePost.as_view(), name='post-like' ) ,
    path('post/<int:pk>/post-dislike', DislikePost.as_view(), name='post-dislike' ) ,
    path('post/<int:pk>/comment-like/<int:comment_pk>', CommentLikeView.as_view(), name='comment-like'),
    path('post/<int:pk>/comment-dislike/<int:comment_pk>', CommentDislikeView.as_view(), name='comment-dislike'),
    #profile_search
    path('profile-search/', SearchProfile.as_view(), name='profile-search'),
    #notification
    path('notification/<int:notification_pk>/post/<int:post_pk>/', PostNotifications.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/profile/', FollowNotification.as_view(), name='follower-notification'),
    path('notification/<int:notification_pk>/remove/' , RemoveNotification.as_view(), name ='remove-notification' ),
    #threads 
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread/', CreateThread.as_view(),name='create-thread'),
    path('inbox/<int:pk>', ThreadView.as_view(),name='thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(),name='create-message'),
    # path('share/<int:pk>/', ShareFormView.as_view(), name='share-post')

    
]  
