from .forms import UploadCSVForm 
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import SecretChild
from django.http import JsonResponse

def call_form(request,message):
    form = UploadCSVForm()
    return render(request, 'employee_upload.html', {'form': form,'message':message}) 

def call_form_secret(request,message):
    form = UploadCSVForm()
    return render(request, 'secretchild_upload.html', {'form': form,'message':message}) 

def generate_new_secret_santa(request,employees,available_employees,previous_assignments):
    assignments = []
    if len(previous_assignments):
            for employee in employees:
                for candidate in available_employees:
                    if candidate.id != employee.id and candidate.id != previous_assignments.get(employee.id):
                        assignments.append((employee, candidate))
                        available_employees.remove(candidate)
                        break
                else:
                    message = "Could not assign secret children. Try again with more people or less strict rules."
                    messages.info(request,message)
                    return False
    else:
        for employee in employees:
            for candidate in available_employees:
                if candidate.id != employee.id:
                    assignments.append((employee, candidate))
                    available_employees.remove(candidate)
                    break
            else:
                message = "Could not assign secret children. Try again with more people or less strict rules."
                messages.info(request,message)
                return False
    return assignments

def update_new_generated_secret_santa(request, assignments):
    previous_year = datetime.now().year - 1
    secret_santa_data = []
    secret_santa_for_current_year = []

    for e, c in assignments:
        secret_santa_data.append(
            {
                'Employee_Name': e.name,
                'Employee_EmailID': e.email,
                'Secret_Child_Name': c.name,
                'Secret_Child_EmailID': c.email,
            }
        )
        secret_santa_for_current_year.append(
            SecretChild(
                employee=e,
                secret_child=c,
                year=previous_year+1
            )
        )

    try:
        SecretChild.objects.bulk_create(secret_santa_for_current_year)
        request.session['secret_santa_data'] = secret_santa_data
        messages.success(request,"For the current year, Secret-santa data created successfully!")
        return redirect('secret_santa')
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)