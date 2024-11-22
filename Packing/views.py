# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from .sticker import Sticker_data
from .models import Sticker
from .forms import StickerForm
from django.http import HttpResponse
from workFlow.DataTransformer import querydict_to_dict
from django.template.loader import render_to_string
from .forms import SearchForm
from Database import SQL_operate


class PackingIndex(TemplateView):
    # 我覺得不用設計登入權限
    template_name = 'Packing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 獲得字典用來傳遞給渲染的頁面
        return context


class StickerListView(LoginRequiredMixin, ListView):
    model = Sticker
    template_name = 'Packing/sticker_list.html'  # 指定你的模板文件

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)

        if form.is_valid():
            # 檢查各個字段是否有有效的搜尋值
            if form.cleaned_data['PROD_NO']:
                queryset = queryset.filter(PROD_NO__icontains=form.cleaned_data['PROD_NO'])
            if form.cleaned_data['material']:
                queryset = queryset.filter(material__icontains=form.cleaned_data['material'])
            if form.cleaned_data['BuyType']:
                queryset = queryset.filter(BuyType__icontains=form.cleaned_data['BuyType'])
            if form.cleaned_data['DSCType']:
                queryset = queryset.filter(DSCType__icontains=form.cleaned_data['DSCType'])
            if form.cleaned_data['color']:
                queryset = queryset.filter(color__icontains=form.cleaned_data['color'])
            if form.cleaned_data['if_BuyType']:
                if form.cleaned_data['if_BuyType'] == '過濾空值':
                    queryset = queryset.filter(BuyType__in=['自印', '外購'])
                else:
                    queryset = queryset.exclude(BuyType__in=['自印', '外購'])
        # 如果沒有提供搜尋條件或條件為空，則返回所有記錄
        return queryset
    
    def get_context_data(self, **kwargs):
        # 建立檢查機制
        app = Sticker_data()
        app.main()
        app.create_sticker_model()
        print("檢查完成")

        context = super().get_context_data(**kwargs)
        context['form'] = StickerForm()
        context['search_form'] = SearchForm()
        # 这里可以添加额外的上下文数据，如果需要的话

        app.out_df.set_index('PROD_NO', inplace=True)
        output_dict = app.out_df['PROD_NAME'].to_dict()
        context['name_map'] = output_dict
        return context


class update_sticker_view(LoginRequiredMixin, View):
    def post(self, request):
        data = querydict_to_dict(request.POST)

        
        app = Sticker_data()
        app.main()
        app.create_sticker_model()
        
        app.out_df.set_index('PROD_NO', inplace=True)
        output_dict = app.out_df['PROD_NAME'].to_dict()
        




        # Initialize the Sticker object with PROD_NO and set other fields
        sticker = Sticker(PROD_NO=data['PROD_NO'])
        sticker.BuyType = data['BuyType']
        sticker.DSCType = data['DSCType'] 
        sticker.heightsize = data['heightsize'] 
        sticker.widthsize = data['widthsize'] 
        sticker.material = data['material']
        sticker.color =  data['color']
        sticker.remark =  data['remark']
        sticker.last_updated_by = request.user 
        sticker.save()
        



        context  = {
            "sticker":sticker,
            "name_map":output_dict,
        }

        # 渲染HTML模板
        html = render_to_string(
            "Packing/sticker_template.html", context, request=request)
        
        return HttpResponse(html)