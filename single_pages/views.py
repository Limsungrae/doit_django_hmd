from django.shortcuts import render

# Create your views here.
def landing(requst):
    return render(
        requst,
        'single_pages/landing.html'
    )
def about_me(requst):
    return render(
        requst,
        'single_pages/about_me.html'
    )
