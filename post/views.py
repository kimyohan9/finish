# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Post, Comment
# from .forms import PostForm, CommentForm

# # 게시글 목록
# def post_list(request):
#     posts = Post.objects.all().order_by('-created_at')
#     return render(request, 'post_list.html', {'posts': posts})

# # 게시글 작성
# @login_required
# def post_create(request):
#     if request.method == "POST":
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('post_list')
#     else:
#         form = PostForm()
#     return render(request, 'post_form.html', {'form': form})

# # 게시글 상세 (댓글 포함)
# def post_detail(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     comments = post.comments.all()

#     if request.method == "POST":
#         if request.user.is_staff:  # 관리자만 댓글 작성 가능
#             form = CommentForm(request.POST)
#             if form.is_valid():
#                 comment = form.save(commit=False)
#                 comment.author = request.user
#                 comment.post = post
#                 comment.save()
#                 return redirect('post_detail', post_id=post.id)
#         else:
#             return redirect('post_detail', post_id=post.id)  # 관리자만 가능하도록 리디렉션
#     else:
#         form = CommentForm()

#     return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, CommentForm
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'post_list.html', {'posts': posts})
@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form})
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    if request.method == "POST":
        if request.user.is_staff:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect('post_detail', post_id=post.id)
        else:
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author or request.user.is_staff:
        post.delete()
        return redirect('post_list')
    else:
        return redirect('post_detail', post_id=post.id)