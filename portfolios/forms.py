from django import forms

PURCHASE_CHOICES = (
    ('BUY', "Buy"),
    ('SELL', "Sell"),
)

class TransactionForm(forms.Form):
    transaction = forms.ChoiceField(required=True, choices=PURCHASE_CHOICES)
    quantity = forms.IntegerField()
    stock = forms.CharField(widget=forms.HiddenInput)

ORDER_CHOICES = (
    ('STOP_LOSS', "Stop Loss"),
    ('LIMIT', 'Limit Order'),
)

LIMIT_CHOICES = (
    ('sell', "Sell"),
    ('buy', "Buy"),
)

class OrderForm(forms.Form):
    order_type = forms.ChoiceField(required=True, choices=ORDER_CHOICES)
    trade_type = forms.ChoiceField(required=False, choices=LIMIT_CHOICES)
    trigger_price = forms.FloatField(required=True, help_text="123.45")
    quantity = forms.IntegerField()
    stock = forms.CharField(widget = forms.HiddenInput)
