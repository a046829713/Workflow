from Company.models import RichText, Form
from django.views.generic import FormView, TemplateView
from .forms import RichText_modelForm
from workFlow.DataTransformer import querydict_to_dict
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.generic import DetailView


class EditFormRichtextView(TemplateView):
    template_name = 'Company/FormRichtext.html'
    # [['123456'], ['123', '456', '789']]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 獲得字典用來傳遞給渲染的頁面
        form_id = self.kwargs.get('form_id')  # 從 URL 參數中獲取 form_id
        form_instance = Form.objects.get(
            form_id=form_id)  # 透過 form_id 查找 Form 實例
        rich_texts = form_instance.rich_text_attachments.all()  # type:ignore
        if rich_texts:
            context['form'] = RichText_modelForm(
                instance=rich_texts.first())  # 假設只編輯第一個實例
        else:
            context['form'] = RichText_modelForm()
        return context

    def post(self, request, *args, **kwargs):
        form_id = self.kwargs.get('form_id')
        form_instance = get_object_or_404(Form, form_id=form_id)
        rich_texts = form_instance.rich_text_attachments.all()  # type:ignore
        rich_text_instance = rich_texts.first() if rich_texts.exists() else None
        rich_text_form = RichText_modelForm(
            request.POST, instance=rich_text_instance)
        if rich_text_form.is_valid():
            rich_text_instance = rich_text_form.save(commit=False)
            rich_text_instance.form = form_instance
            rich_text_instance.save()
            messages.success(request, '更新成功！')
            redirect_url = reverse('form_information', args=[form_id])
            return redirect(redirect_url)

        return self.render_to_response(self.get_context_data(form=rich_text_form))


class ShowRichTextView(DetailView):
    model = RichText
    template_name = 'Company/Richtextshow.html'  # 使用新的模板
    context_object_name = 'richtext'

    def get_object(self, queryset=None):
        form_id = self.kwargs.get('form_id')
        form_instance = get_object_or_404(Form, form_id=form_id)
        rich_texts = form_instance.rich_text_attachments.all()  # type:ignore
        rich_text_instance = rich_texts.first() if rich_texts.exists() else None
        return rich_text_instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里您可以添加任何额外的上下文您认为需要传递给模板的
        return context
