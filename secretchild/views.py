import csv
import random, pandas as pd, openpyxl
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Employee, SecretChild
from .forms import UploadCSVForm 
from datetime import datetime
from django.contrib import messages
from .common_code import call_form, call_form_secret, generate_new_secret_santa, update_new_generated_secret_santa

def secret_santa(request):
    data = request.session.get('secret_santa_data')
    if data:
        return render(request, 'index.html',{"generate_flag":True})
    else:
        return render(request, 'index.html')

def upload_employee_csv(request):
    """Handle the employee CSV upload."""
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            read_function = pd.read_csv
        elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
            read_function = pd.read_excel
        else:
            message = 'Only accept the csv or excel file format'
            return call_form(request,message)

        try:
            employees = read_function(file)
        except Exception as e:
            return JsonResponse({'Error handling': str(e)}, status=400)

        original_rows = employees.shape[0]
        employees = employees.dropna(axis=0, how="any")
    
        if original_rows > employees.shape[0]:
            message = 'The employee file all column should have value'
            return call_form(request,message)
        
        required_columns = {"Employee_Name", "Employee_EmailID"}
        if required_columns.issubset(employees.columns):
            employees = employees.drop_duplicates(subset=['Employee_EmailID'], keep='first')
        else:
            message = "The employee file columns must have 'Employee_Name', 'Employee_EmailID'."
            return call_form(request,message)

        employees = employees.to_dict(orient='records')

        existing_employees = Employee.objects.values_list('email', flat=True)

        try:
            employee_instances = [
                Employee(
                    name=employee['Employee_Name'],
                    email=employee['Employee_EmailID']
                )
                for employee in employees
                if str(employee['Employee_EmailID']) not in existing_employees]
        except Exception as e:
            return JsonResponse({'Data class error handling': str(e)}, status=400)
        
        try:
            if len(employee_instances):
                Employee.objects.bulk_create(employee_instances)
                messages.success(request,"Employees data created successfully!")
                return redirect('secret_santa')
            else:
                message = "There is not new employee date in the employee csv file"
                return call_form(request,message)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        form = UploadCSVForm()
    return render(request, 'employee_upload.html', {'form': form})

def upload_previous_secretchild_data(request):
    """Handle previous year's assignment CSV upload using Pandas."""
    if request.method == 'POST' and request.FILES['file']:

        file = request.FILES['file']
        if file.name.endswith('.csv'):
            read_function = pd.read_csv
        elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
            read_function = pd.read_excel
        else:
            message = 'Only accept the csv or excel file format'
            return call_form_secret(request,message)

        try:
            secretchild = read_function(file)
        except Exception as e:
            return JsonResponse({'Error handling': str(e)}, status=400)

        original_rows = secretchild.shape[0]
        secretchild = secretchild.dropna(axis=0, how="any")
    
        if original_rows > secretchild.shape[0]:
            message = 'The employee file all column should have value'
            return call_form_secret(request,message)
        
        required_columns = {"Employee_Name", "Employee_EmailID","Secret_Child_Name", "Secret_Child_EmailID"}
        if required_columns.issubset(secretchild.columns):
            secretchild = secretchild.drop_duplicates(subset=['Employee_EmailID','Secret_Child_EmailID'], keep='first')
            if original_rows > secretchild.shape[0]:
                message = 'We found some duplicate date in the file'
                return call_form_secret(request,message)
        else:
            message = "The employee file columns must have 'Employee_Name', 'Employee_EmailID'."
            return call_form_secret(request,message)

        secretchild = secretchild.to_dict(orient='records')

        previous_year = int(datetime.now().year) - 1

        employee_instances = []
        try:
            existing_secretchild = SecretChild.objects.select_related('employee','secret_child').filter(year=previous_year)
            if existing_secretchild.count():
                if existing_secretchild.count() == original_rows:
            
                    existing_secretchild_dict = {secretchild.employee.email:{"employee_id":secretchild.employee.email,"secretchild_id":secretchild.secret_child.email,"year":secretchild.year} for secretchild in existing_secretchild}
                    for child in secretchild:
                        if child['Employee_EmailID'] not in existing_secretchild_dict or child['Secret_Child_EmailID'] != existing_secretchild_dict[child['Employee_EmailID']]['secretchild_id']:
                            message = "Compare to previous secret-santa we found some changes in secret-santa details in the uploaded file."
                            return call_form_secret(request,message)
                else:
                    message = "Previous secret-santa child data is missing from the uploaded file."
                    return call_form_secret(request,message)
            else:
                existing_employees = Employee.objects.all()
                if not existing_employees:
                    messages.error(request, "Unable to upload the previous secret-santa child without employee details!!. Please first upload the employee details")
                    return redirect('secret_santa')
                existing_employees_dict = {employee.email:employee for employee in existing_employees}
                for employee in secretchild:
                    if str(employee['Employee_EmailID']) in existing_employees_dict and str(employee['Secret_Child_EmailID']) in existing_employees_dict:
                        employee_instances.append(
                            SecretChild(
                                employee=existing_employees_dict[str(employee['Employee_EmailID'])],
                                secret_child=existing_employees_dict[str(employee['Secret_Child_EmailID'])],
                                year= previous_year
                            )
                        )
        except Exception as e:
            return JsonResponse({'Data class error handling': str(e)}, status=400)
        
        try:
            if len(employee_instances):
                SecretChild.objects.bulk_create(employee_instances)
                message = "For the previous year, Secret-santa data created successfully!"
                messages.success(request,message)
                return redirect('secret_santa')
            else:
                message = "The uploaded secret-santa data's are match. You can generate secret-santa for current year!!"
                messages.success(request,message)
                return redirect('secret_santa')
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        form = UploadCSVForm()
    return render(request, 'secretchild_upload.html', {'form': form})

def assign_secret_santa_children(request):
    previous_year = datetime.now().year - 1
    employees = list(Employee.objects.all())

    if not employees:
        messages.error(request, "Unable to generate secret-santa child without employee details!!. Please first upload the employee details")
        return redirect('secret_santa')

    previous_assignments = {
        a.employee.id: a.secret_child.id
        for a in SecretChild.objects.filter(year=previous_year)
    }

    available_employees = employees[:]
    random.shuffle(available_employees)
    assignments = []

    current_secret_santa = SecretChild.objects.select_related('employee','secret_child').filter(year=previous_year+1)
    secret_santa_data = []
    if current_secret_santa:
        if len(employees) > len(current_secret_santa):
            try:
                SecretChild.objects.filter(year=previous_year+1).delete()
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
            
            assignments = generate_new_secret_santa(request,employees,available_employees,previous_assignments)
            if assignments:
                update_new_generated_secret_santa(request, assignments)
                return redirect('secret_santa')
            else:
                return redirect('secret_santa')
        else:
            for secret_sanda in current_secret_santa:
                secret_santa_data.append(
                    {
                        'Employee_Name': secret_sanda.employee.name,
                        'Employee_EmailID': secret_sanda.employee.email,
                        'Secret_Child_Name': secret_sanda.secret_child.name,
                        'Secret_Child_EmailID': secret_sanda.secret_child.email,
                    }
                )
    else:
        assignments = generate_new_secret_santa(request,employees,available_employees,previous_assignments)
        if assignments:
            update_new_generated_secret_santa(request, assignments)
            return redirect('secret_santa')
        else:
            return redirect('secret_santa')
        
    request.session['secret_santa_data'] = secret_santa_data
    messages.success(request, "Secret Santa assignments generated successfully!")
    return redirect('secret_santa')

def download_secret_santa_csv(request):
    data = request.session.get('secret_santa_data')
    if not data:
        messages.error(request, "No Secret Santa data found to download.")
        return redirect('secret_santa')
    
    request.session['secret_santa_data'] = ""

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="secret_santa_assignments.csv"'
    df.to_csv(response, index=False)
    return response
