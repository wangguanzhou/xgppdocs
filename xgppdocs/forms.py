from django import forms

class TDocFilter(forms.Form):
    #def __init__(self, *args, **kwargs):
    #    source_choices = kwargs.pop('source_choices')
    #    super(TDocFilter, self).__init__(*args, **kwargs)
    #    self.fields['tdoc_source'] = forms.ChoiceField(choices=source_choices)
    meeting_no = forms.CharField(
        label='',
        widget=forms.HiddenInput(),
    )
    tdoc_source = forms.ChoiceField(
        label='',
        widget=forms.Select(),
    )
    tdoc_type = forms.ChoiceField(
        label='',
        widget=forms.Select(),
    )
    tdoc_agendaitem = forms.MultipleChoiceField(
        label='',
        widget=forms.Select(),
    )
    tdoc_status = forms.MultipleChoiceField(
        label='',
        widget=forms.Select(),
    )
    
    