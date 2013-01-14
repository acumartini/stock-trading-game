from django import forms

from stocks.models import Stock

class SearchForm(forms.Form):
    ticker = forms.CharField(max_length=5)
    
