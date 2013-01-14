from django import forms

TYPE_CHOICES = (
    ('RandomAgent', 'Random Agent'),
    ('DiverseRandomAgent', 'Diverse Random Agent'),
    ('Top20Agent', 'Top 20 Agent'),
    ('HighVolumeAgent', 'High Volume Agent'),
    ('BuyHighSellHighAgent', 'Buy High Sell High Agent'),
    ('BuyHighSellLowAgent', 'Buy High Sell Low Agent'),
    ('BuyLowSellHighAgent', 'Buy Low Sell High Agent'),
    ('BuyLowSellLowAgent', 'Buy Low Sell Low Agent'),
    # ('IntelligentAgent', 'Intelligent Agent')
)

AGGRESSION_CHOICES = (
    ('Normal', 'Normal'),
    ('Aggressive', 'Aggressive'),
    ('Lazy', 'Lazy')
)

class CreateAgentForm(forms.Form):
    agent_name = forms.SlugField(required=True, help_text="Only letters, numbers, '_', and '-' are allowed.")
    agent_type = forms.ChoiceField(choices=TYPE_CHOICES)
    agent_aggression = forms.ChoiceField(choices=AGGRESSION_CHOICES)
    game_pk = forms.IntegerField(widget = forms.HiddenInput)
