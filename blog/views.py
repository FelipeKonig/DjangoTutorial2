from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment, PostLike, PostDislike
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save()

    liked = False
    disliked = False

    if request.user.is_authenticated:
        likes_count = PostLike.objects.filter(
            post_id=pk,
            user=request.user
        ).count()
        if likes_count > 0:
            liked = True

        dislikes_count = PostDislike.objects.filter(
            post_id=pk,
            user=request.user
        ).count()
        if dislikes_count > 0:
            disliked = True

    try:
        percentApproved = post.likes_count() / ( post.likes_count() + post.dislikes_count()) * 100
        percentDisapproved = post.dislikes_count() / ( post.dislikes_count() +  post.likes_count()) * 100
    except:
        percentApproved = 0
        percentDisapproved = 0

    return render(request,
    'blog/post_detail.html',
     {'post': post, 'liked': liked, 'disliked': disliked,
      'percentApproved': percentApproved, 'percentDisapproved': percentDisapproved}
    )

@login_required
def post_new(request):
     if request.method == "POST":
         form = PostForm(request.POST)
         if form.is_valid():
             post = form.save(commit=False)
             post.author = request.user
             post.save()
             return redirect('post_detail', pk=post.pk)
     else:
         form = PostForm()
     return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
     post = get_object_or_404(Post, pk=pk)
     if request.method == "POST":
         form = PostForm(request.POST, instance=post)
         if form.is_valid():
             post = form.save(commit=False)
             post.author = request.user
             post.save()
             return redirect('post_detail', pk=post.pk)
     else:
         form = PostForm(instance=post)
     return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

def publish(self):
    self.published_date = timezone.now()
    self.save()

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

@login_required
def post_like(request, pk):
    postLike, created = PostLike.objects.get_or_create(
        post_id=pk,
        user=request.user
    )

    return redirect('post_detail', pk=pk)

@login_required
def post_dislike(request, pk):
    postDislike, created = PostDislike.objects.get_or_create(
        post_id=pk,
        user=request.user
    )

    return redirect('post_detail', pk=pk)

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)
