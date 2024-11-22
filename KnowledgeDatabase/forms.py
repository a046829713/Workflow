from django import forms
from django_select2.forms import Select2MultipleWidget
from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import KnowledgeDatabase_model

class KnowledgeDatabaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        TAGS_CHOICES = kwargs.pop('tags_choices', [])
        super(KnowledgeDatabaseForm, self).__init__(*args, **kwargs)
        self.fields['Tags'] = forms.MultipleChoiceField(
            choices=TAGS_CHOICES,
            label="標籤選擇(可複選)",
            widget=Select2MultipleWidget(attrs={'class': 'form-control', 'id': 'Tags_control'})
        )
    
    PRIVACY_CHOICES = [
        ('公開', '公開'),
        ('不公開', '不公開'),

    ]
    
    project_name = forms.CharField(
        label="文章名稱",
        widget=forms.TextInput(attrs={'class': 'form-control mt-2',
                                       'placeholder': '請輸入文章名稱'}))

    privacy = forms.ChoiceField(
        label="隱私",
        choices=PRIVACY_CHOICES,
        widget=forms.RadioSelect
    )
    

class KnowledgeDatabase_modelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        TAGS_CHOICES = kwargs.pop('tags_choices', [])        
        super(KnowledgeDatabase_modelForm, self).__init__(*args, **kwargs)        
        self.fields['tags'] = forms.MultipleChoiceField(
            choices=TAGS_CHOICES,
            label="標籤選擇(可複選)",
            widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'Tags_control'})
        )
        
            
    class Meta:
        model = KnowledgeDatabase_model
        fields = ['project_name', 'tags', 'content']
        
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='awesome_ckeditor'))
    