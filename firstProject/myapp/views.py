from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import Student
import datetime

def listone(request, student_name=None):
    try:
        # 如果未提供學生姓名，默認顯示"潘驄杰"
        if student_name is None:
            student_name = "潘驄杰"
            
        unit = Student.objects.get(sName=student_name)  # 讀取一筆資料
    except Exception as e:
        errormessage = f"找不到名為 {student_name} 的學生！"
        return render(request, "myapp/Listone.html", {'errormessage': errormessage})
    return render(request, "myapp/Listone.html", {'unit': unit})

def listall(request):
    allstudents = Student.objects.all().order_by('id')
    return render(request, "myapp/listall.html", locals())


def sayhello3(request, showname):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render(request, 'myapp/welcome.html', {
        'name': showname,
        'current_time': current_time
    })

def sayhello4(request, showname):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render(request, 'myapp/sayhello4.html', {
        'name': showname,
        'current_time': current_time
    })



