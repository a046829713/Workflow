from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group

def group_required(group_name:list):
    """
    用來檢查使用者的group是否與限制者相同
    """
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # 判斷每一個權限
            for each_Group_name in group_name:
                print("每個權限:", each_Group_name)
                print(request.user)
                if request.user.groups.filter(name=each_Group_name).exists():
                    # 成功的話進入
                    return view_func(request, *args, **kwargs)

            # 當每一個使用者權限都失效的時候
            # 失敗的話進入
            return  redirect('forbidden')
        return _wrapped_view
    return decorator



class GroupRequiredMixin(UserPassesTestMixin):
    group_required = None

    def test_func(self):
        if self.group_required is None:
            return False

        return Group.objects.filter(name__in=self.group_required, user=self.request.user).exists() # type: ignore

    def handle_no_permission(self):
        return redirect('forbidden')