from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from django.db.models import Q
from .forms import PostForm, CommentForm
# new_comment 구현
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

# from .forms import PostForm
# Create your views here.
# def index(request) :
#     posts = Post.objects.all().order_by('-pk')

#     return render(
#         request,
#         'blog/index.html',
#         {
#             'posts':posts,
#         }
#     )
# 댓글 수정 클래스 생성
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate,self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied




# urls.py의 update_post 주소에 보일 뷰 생성, 수정하는곳
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title','hook_text','content','head_image','file_upload','category']

    template_name = 'blog/post_update_form.html'

    # 태그 값 가져오기
    def get_context_data(self, **kwargs ):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] ='; '.join(tags_str_list)
        return context
    
    def form_valid(self, form):
        response = super(PostUpdate,self).form_valid(form)
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str =tags_str.strip()

            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response






    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


    
def new_comment(request, pk):
    #  # 로그인하지 않았다면 PermissionDenied 권한이 거부됨
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        # method가 POST일경우 CommentForm 값을 불러온다
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                # 작성버튼 누르면 페이지로 리다이렉트
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
       
        raise PermissionDenied
    
    

# is_superuser 만 글작성 가능하게 함
# 태그 선택란 추가 
class PostCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    # fields = ['title','hook_text','content','head_image','file_upload','category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            # return super(PostCreate, self).form_valid(form)

        
        # 태그 input  구성하기
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str =tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')






def tag_page(request,slug):
    tag = Tag.objects.get(slug=slug)
    post_list= tag.post_set.all()

    return render(
            request,
            'blog/post_list.html',
            {
                'post_list':post_list,
                'tag': tag,
                'categories': Category.objects.all(),
                'no_category_post_count':Post.objects.filter(category=None).count(),
            }
        )

def category_page(request,slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
            request,
            'blog/post_list.html',
            {
                'post_list': post_list,
                'categories':Category.objects.all(),
                'no_category_post_count': Post.objects.filter(category=None).count(),
                'category': category,
            }
        )
        
class PostList(ListView):
    model = Post
    ordering = '-pk'

    # 한 페이지를 보여줄 post 객수 정하기
    paginate_by = 3


    def get_context_data(self, **kwargs ):
        context = super(PostList, self).get_context_data()
        context['categories'] =  Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
    
class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q =self.kwargs['q']
        post_list= Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)        
        ).distinct()
        return post_list
    def get_context_data(self, **kwargs):
        context = super(PostSearch,self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'
        
        return context
    # def category_page(request, slug):
    #     context ={}
    #     category = Category.objects.get(slug=slug)
    #     context['post_list'] = Post.objects.filter(category=category)
    #     context['categories'] =  Category.objects.all()
    #     context['no_category_post_count'] = Post.objects.filter(category=None).count()
    #     context['category'] = category

    #     return render(
    #         request,
    #         'blog/post_list.html',
    #         context
    #     )







class PostDetail(DetailView):
    model = Post
    def get_context_data(self, **kwargs ):
        context = super(PostDetail, self).get_context_data()
        context['categories'] =  Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context

# def single_post_page(request, pk) :
#     post = Post.objects.get(pk=pk)

#     return render(
#         request,
#         'blog/single_post_page.html',
#         {
#             'post':post,
#         }
#     )


