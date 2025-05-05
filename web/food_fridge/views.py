from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def new_food(request):
  template = loader.get_template('new_food.html')
  return HttpResponse(template.render())


