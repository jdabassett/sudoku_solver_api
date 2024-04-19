from django.urls import path
from .views import Sudoku_API

urlpatterns = [
    path('solve/', Sudoku_API.as_view() ,name='solve'),
]