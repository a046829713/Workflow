from schedule.models import Event,Visitor
from django.views.generic import ListView
import datetime
from Company.models import Employee

class GuardRoomView(ListView):
    model = Event
    template_name = "schedule/guard_room.html"
    context_object_name = "events"  # 在模板中使用的上下文对象的名称
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        # 我只要創建人是自己才顯示
        queryset = super().get_queryset()
        today = datetime.datetime.today().date()  # 只保留日期部分
        queryset = queryset.filter(
            start__date__lte=today,  # 事件的开始日期在今天或之前
            end__date__gte=today      # 事件的结束日期在今天或之后
        )
        
        # 遍历每个 event 并添加新的属性或键值对
        for event in queryset:
            event.visitor = Visitor.objects.get(id = event.form_without_view.split('-')[0])
            event.unit = (Employee.objects.get(worker_id = event.creator.username).unit)
            
        return queryset