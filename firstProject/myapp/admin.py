from django.contrib import admin
from myapp.models import Student

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sName', 'sSex', 'sBirthday', 'sEmail', 'sPhone', 'sAddress')
    list_filter = ('sSex', 'sBirthday')  # 更改篩選欄位以提供更有用的篩選
    search_fields = ('sName', 'sEmail', 'sPhone')  # 擴展搜尋範圍
    ordering = ('id',)
    list_per_page = 10  # 每頁顯示數量
    date_hierarchy = 'sBirthday'  # 增加日期層級瀏覽
    
    # 增加欄位分組顯示
    fieldsets = (
        ('基本資料', {
            'fields': ('sName', 'sSex', 'sBirthday')
        }),
        ('聯絡資訊', {
            'fields': ('sEmail', 'sPhone', 'sAddress')
        }),
    )

admin.site.register(Student, StudentAdmin)

