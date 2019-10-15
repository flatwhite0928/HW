from django.views.decorators import csrf
from django.shortcuts import render, render_to_response


def start(request):
    return render_to_response('helloworld.html')