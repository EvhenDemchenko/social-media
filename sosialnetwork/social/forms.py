
from django import forms
from django.forms import widgets
from .models import MessageModel, Post, Comment, UserProfile


# issue for multi_upload images
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
# issue for multi_upload images


class PostForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control ', 'rows': 10, 'style': 'height: 200px; '})
    )

    image = MultipleFileField(required=False)

    # if you modify the form class you have to add the "image" field to fields
    class Meta:
        model = Post
        fields = ['body']


class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 1}))

    class Meta:
        model = Comment
        fields = ['comment']


class ProfileForm(forms.ModelForm):
    name = forms.CharField()
    bio = forms.Textarea()
    birth_date = forms.DateInput()
    location = forms.CharField()
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['name', 'bio', 'birth_date', 'location', 'picture']


class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)


class MessageForm(forms.ModelForm):
    body = forms.CharField(label='', max_length=1000)
    image = forms.ImageField(required=False)

    class Meta:
        model = MessageModel
        fields = ['body', 'image']

# class ShareForm(forms.Form):


class ShareForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(
        attrs={
            "rows":'3',
            "placeholder":'Say something'
        }
    ))  
