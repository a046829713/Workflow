from django import forms
from .models import Sticker



class SearchForm(forms.Form):
    PROD_NO = forms.CharField(
        required=False, label='產品編號',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    material = forms.ChoiceField(
        choices=[('', '選擇材質')] + list(Sticker.MATERIAL_CHOICES),
        required=False, label='材質',
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    BuyType = forms.ChoiceField(
        choices=[('', '選擇購買類型')] + list(Sticker.BUY_TYPE_CHOICES),
        required=False, label='購買類型',
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    DSCType = forms.ChoiceField(
        choices=[('', '選擇描述類型')] + list(Sticker.DSC_TYPE_CHOICES),
        required=False, label='描述類型',
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    color = forms.ChoiceField(
        choices=[('', '選擇顏色')] + list(Sticker.COLOR_CHOICES),
        required=False, label='顏色',
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    if_BuyType = forms.ChoiceField(
        choices=[('', '選擇篩選條件'),('過濾空值', '過濾空值'),('保留空值', '保留空值')],
        required=False, label='空值過濾',
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )


class StickerForm(forms.ModelForm):
    class Meta:
        model = Sticker
        fields = '__all__'  # 这将包含模型中的所有字段
        labels = {
            'PROD_NO': '產品編號',
            'BuyType': '購買類型',
            'DSCType': '描述類型',
            'heightsize': '高度大小',
            'widthsize': '寬度大小',
            'material': '材質',
            'color': '顏色',
            'remark': '備註',
            'image': '圖片'
        }
        widgets = {
            'PROD_NO': forms.TextInput(attrs={'class': 'form-control', 'id': "target_prod_no", 'readonly': 'readonly'}),
            'BuyType': forms.Select(attrs={'class': 'form-control select2'}),
            'DSCType': forms.Select(attrs={'class': 'form-control select2'}),
            'heightsize': forms.NumberInput(attrs={'class': 'form-control'}),
            'widthsize': forms.NumberInput(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control select2'}),
            'color': forms.Select(attrs={'class': 'form-control select2'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
