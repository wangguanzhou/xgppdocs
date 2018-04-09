from django import forms

class TDocFilter(forms.Form):
    tdoc_source = forms.ChoiceField(
        label='',
        widget=forms.Select(
            attrs={
                'class': 'ui fluid dropdown',
            }
        ),
    )
    tdoc_type = forms.ChoiceField(
        label='',
        initial='Type',
        widget=forms.Select(),
    )
    tdoc_agendaitem = forms.ChoiceField(
        label='',
        initial='Agenda Item',
        widget=forms.Select(),
    )
    tdoc_status = forms.ChoiceField(
        label='',
        initial='Status',
        widget=forms.Select(),
    )
    
    