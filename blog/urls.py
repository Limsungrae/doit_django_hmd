from django.urls import path
from .import views

urlpatterns = [
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    # /blog/
    path('',views.PostList.as_view()),
    #/blog/1
    path('<int:pk>/',views.PostDetail.as_view()),
    # path('<int:pk>/',views.single_post_page),
    # path('',views.index),
    path('category/<str:slug>/',views.category_page),
    path('tag/<str:slug>/',views.tag_page),
    path('<int:pk>/new_comment/',views.new_comment),
    # 수정 페이지인 update_post url 생성  
    path('update_post/<int:pk>/',views.PostUpdate.as_view()),
    # 댓글 수정 url 생성
    path('update_comment/<int:pk>/',views.CommentUpdate.as_view()),

]

