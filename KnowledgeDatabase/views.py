from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from workFlow.DataTransformer import querydict_to_dict
from .forms import KnowledgeDatabaseForm
from .models import KnowledgeDatabase_model
import json
import random
from django.http import HttpResponseNotFound
from django.views.generic.detail import DetailView
# from .forms import CommentForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView,TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import KnowledgeDatabase_modelForm
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from Company.models import Employee
from django.db.models import Q
from. Datatransformer import Datatransformer
from Company.models import CustomUser
from workFlow.Appsettings import DEPARTMENT_AUTHORITY

class ArticleListView(LoginRequiredMixin, ListView):
    model = KnowledgeDatabase_model
    template_name = "KnowledgeDatabase/Knowledeg_index.html"
    context_object_name = 'kd_list'
    paginate_by = 10  # 每页显示的对象数量
    
    def _random_color(self):
        """生成随机颜色的函数"""
        return "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])

    def privacy_check(self, request, each_data):
        if each_data.privacy == '公開':
            return True

        unit = Datatransformer().clean_unit(Employee.objects.get(worker_id=request.user).unit)
        permission_unit = Datatransformer().find_department_path(DEPARTMENT_AUTHORITY, unit)
        each_data_unit = Datatransformer().find_department_path(DEPARTMENT_AUTHORITY, each_data.unit)
        check_if_unit = any(_unit in permission_unit[1:] for _unit in each_data_unit[1:])
        return check_if_unit and len(permission_unit) <= len(each_data_unit)

    def get_queryset(self):
        queryset = super().get_queryset()
        return [each_data for each_data in queryset if self.privacy_check(self.request, each_data)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kd_lists = context['kd_list']

        all_tags = list(set([tag for each_data in kd_lists for tag in json.loads(each_data.tags)]))
        tagged_colors = {tag: self._random_color() for tag in all_tags}

        for each_data in kd_lists:
            each_data.tags = json.loads(each_data.tags)

        form = KnowledgeDatabaseForm(tags_choices=[(tag, tag) for tag in all_tags])

        context.update({
            'form': form,
            'tagged_colors': tagged_colors,
            'all_tags': all_tags,
            "fullname_map": {kd.applicant: CustomUser.objects.get(username=kd.applicant).FullName for kd in kd_lists}
        })
        return context

    def post(self, request, *args, **kwargs):
        post_data = request.POST.dict()
        searchTerm = post_data.get('searchTerm', '')
        
        kd_lists = KnowledgeDatabase_model.objects.filter(
            Q(unit__icontains=searchTerm) | 
            Q(tags__icontains=json.dumps(searchTerm))|
            Q(project_name__icontains=searchTerm)
            
        )
        
        all_tags = list(set([tag for each_data in kd_lists for tag in json.loads(each_data.tags)]))
        tagged_colors = {tag: self._random_color() for tag in all_tags}

        for each_data in kd_lists:
            each_data.tags = json.loads(each_data.tags)

        kd_lists = [each_data for each_data in kd_lists if self.privacy_check(request, each_data)]

        form = KnowledgeDatabaseForm(tags_choices=[(tag, tag) for tag in all_tags])

        context = {
            'form': form,
            'kd_list': kd_lists,
            'tagged_colors': tagged_colors,
            "fullname_map": {kd.applicant: CustomUser.objects.get(username=kd.applicant).FullName for kd in kd_lists}
        }
        return render(request, "KnowledgeDatabase/Knowledeg_index.html", context)


class AddArticleView(View):
    def post(self, request, *args, **kwargs):
        post_data = querydict_to_dict(request.POST)
        KD = KnowledgeDatabase_model()
        KD.project_name = post_data['project_name']
        KD.tags = json.dumps(post_data['Tags']) if isinstance(post_data['Tags'],list) else json.dumps([post_data['Tags']])
        KD.applicant = request.user
        KD.unit = Datatransformer().clean_unit(Employee.objects.get(worker_id = request.user).unit)
        KD.privacy = post_data['privacy']
        KD.save()
        return redirect('article-list')

class EditArticleView(TemplateView):
    template_name = 'KnowledgeDatabase/Article.html'  
    # [['123456'], ['123', '456', '789']]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 獲得字典用來傳遞給渲染的頁面
        Article_id = kwargs['pk']
        article_instance = KnowledgeDatabase_model.objects.get(pk =Article_id)
        # 將資料傳入model form 然後傳入前端頁面
        kd_lists = KnowledgeDatabase_model.objects.all()
        all_tags = [json.loads(each_data.tags) for each_data in kd_lists]
        all_tags = list(set([item for sublist in all_tags for item in sublist]))        
        context['form'] = KnowledgeDatabase_modelForm(tags_choices=[(tag, tag) for tag in all_tags],  instance=article_instance)
        context['select_list'] = article_instance.tags
        return context

    def post(self, request, *args, **kwargs):
        Article_id = kwargs['pk'] 
        post_data = querydict_to_dict(request.POST)
        KD = KnowledgeDatabase_model.objects.get(pk=Article_id)
        KD.project_name = post_data['project_name']
        KD.tags = json.dumps(post_data['tags']) if isinstance(post_data['tags'],list) else json.dumps([post_data['tags']])
        KD.content = post_data['content']
        KD.save()
        return redirect('article-list')



class DeleteArticleView(View):
    def post(self, request, *args, **kwargs):
        Article_id = kwargs['pk']
        KnowledgeDatabase_model.objects.get(pk=Article_id).delete()
        return redirect('article-list')



from django.views.generic import DetailView

class ShowArticleView(DetailView):
    model = KnowledgeDatabase_model
    template_name = 'KnowledgeDatabase/ArticleShow.html'  # 使用新的模板
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 这里您可以添加任何额外的上下文您认为需要传递给模板的
        return context