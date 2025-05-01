import os
import sys
import django
import datetime

# 將上級目錄添加到 Python 路徑，以便找到 firstProject 模塊
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstProject.settings')
django.setup()

from myapp.models import Student

# 要添加的學生資料
students = [
    {'id': '11144209', 'name': '潘驄杰', 'sex': 'M'},
    {'id': '11144272', 'name': '劉曦鴻', 'sex': 'M'},
    {'id': '11144256', 'name': '王盛峰', 'sex': 'M'},
    {'id': '11144225', 'name': '蔡曉慧', 'sex': 'F'},
    {'id': '11144206', 'name': '阮祐華', 'sex': 'M'},
]

# 為所有學生使用相同的出生日期（這裡只是範例，實際使用時應該使用真實數據）
default_birthday = datetime.date(2000, 1, 1)

# 添加學生到資料庫
def add_students():
    for student in students:
        # 檢查學生是否已存在（根據姓名檢查）
        if not Student.objects.filter(sName=student['name']).exists():
            # 創建新學生記錄
            Student.objects.create(
                sName=student['name'],
                sSex=student['sex'],
                sBirthday=default_birthday,
                sEmail=f"{student['id']}@cycu.edu.tw",  # 使用學號創建示例郵箱
                sPhone='',
                sAddress=''
            )
            print(f"已添加學生: {student['name']}")
        else:
            print(f"學生 {student['name']} 已存在，跳過")

if __name__ == "__main__":
    print("開始添加學生...")
    add_students()
    print("學生添加完成！") 