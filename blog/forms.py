# CommentForm구현하기
from.models import Comment
from django import forms

# post form
from django import forms
from .models import Post

from django_summernote.widgets import SummernoteWidget

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('post', 'author', 'creat_at', 'modified_at',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'hook_text','content','head_image','file_upload','category']
        widgets = {
            'content': SummernoteWidget(),
        }