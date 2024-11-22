from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from workFlow.DataTransformer import querydict_to_dict
from django.shortcuts import render
from .forms import AssembleWmodelForm
from .W_modwl import Papertube,Roller,Productno,Pulltheblackball,Gear,Foam,Handle,Bendpipe,Cover,ModelMergeTool

# Create your views here.


class AssembleWmodel(LoginRequiredMixin, View):
    def get(self, request):
        form = AssembleWmodelForm()
        context = {
            'form':form
        }
        
        return render(request, "AssembleWmodel/AssembleWmodel.html", context)

    def post(self, request):
        

        data = querydict_to_dict(request.POST)
        
        
        # print(Papertube(data).mergedata) # 紙管(膠膜)        
        # print(Roller(data).mergedata) # 滾輪款式
        # print(Productno(data).mergedata) # 鐵條款式        
        # print(Pulltheblackball(data).mergedata) # 拉把黑球
        # print(Gear(data).mergedata) # 齒輪        
        # print(Cover(data).mergedata) # 上下蓋
         

                
        # 泡棉
        # 手炳握把
        # 彎管
        mergertool = ModelMergeTool()
        mergertool.merge_Foam_Handle_Bendpipe(Foam(data),Handle(data),Bendpipe(data))
        
        
        mergertool.rule(Papertube(data),Roller(data),Productno(data),Pulltheblackball(data),Gear(data),Cover(data))
        
        return render(request, "Company/index.html")
