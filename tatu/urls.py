from django.urls import path
from .views import search_answers
from .tatu import search_answer
from .claude import search_answerc

urlpatterns = [
    path('api/search/',search_answer, name='search_answers'),
    path('search/', search_answers, name='search_answer'),
    path('search/claude', search_answerc, name='search_answerc'),

]


