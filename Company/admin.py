from django.contrib import admin
from .models import CustomUser, Level, Form
from django.contrib.auth.admin import UserAdmin

# 用來將http://127.0.0.1:8000/admin 的相關表單做更改

# UserAdmin 是 ModelAdmin 的一個子類，已經包含了很多適合用戶模型的特性，比如處理密碼字段的邏輯。
# 使用 UserAdmin 可以避免你手動寫很多常見的邏輯。
# class CustomUserAdmin(admin.ModelAdmin):


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
        用來管理Admin上面的表單狀態
        為甚麼要使用UserAdmin管理是因為,裡面已經有內建很多密碼的設定比較方便,
        在Django裡面使用hash來處理

        for simplify password authentication  change settings.py AUTH_PASSWORD_VALIDATORS
        在改變了密碼驗證規則後，UserAdmin 還是可以正常工作的，因為它在保存密碼時並不直接使用驗證器，而是通過 set_password 方法，這個方法不會受到驗證器的影響。驗證器只在調用 validate_password 函數時使用，UserAdmin 不會直接調用這個函數。但是，如果你在其他地方（如表單或視圖）使用了 validate_password 函數，那麼就會受到新的驗證規則的影響。
    Args:
        exclude:排除不要的字段
    """
    # exclude = ('date_joined', 'first_name', 'last_name', 'last_login')
    # list_filter = ()

    # 用來展示admin的列表
    list_display = ('username', 'FullName', 'email',
                    'is_active', 'is_staff', 'group_names')

    # 由於可能會有多個群組,所以要這樣顯示
    def group_names(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    group_names.short_description = 'Groups'  # 设置列的标题

    # 前面是標題列,後面是需要顯示的字段
    fieldsets = (
        ('Accout', {'fields': ('username', 'password')}),
        ("User Information", {
         'fields': ('email', 'FullName', 'groups', 'is_active')})
    )


    # 也可以加入搜索和過濾的功能，以下只是一個示例
    search_fields = ['username','FullName'] 

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = (
        'level_id', 'level_name', 'station_name', 'next_station', 
        'previous_station', 'station_choice', 'station_manager', 
        'station_group', 'station_mode', 'endorsement_manager', 
        'endorsement_group', 'endorsement_mode', 'limited_time', 'versionNumber'
    )

    # 也可以加入搜索和過濾的功能，以下只是一個示例
    search_fields = ['level_name'] 
    list_filter = ['level_name'] 


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('form_id', 'form_name', 'applicant', 'result', 'application_date', 'closing_date', 'version_number')
    search_fields = ('form_id', 'form_name', 'applicant')