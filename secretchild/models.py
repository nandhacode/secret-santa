from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'employee'
        verbose_name = "employee" 
        verbose_name_plural = "employees"

class SecretChild(models.Model):
    employee = models.ForeignKey(Employee, related_name='parent', on_delete=models.CASCADE)
    secret_child = models.ForeignKey(Employee, related_name='child', on_delete=models.CASCADE)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.employee.name} -> {self.secret_child.name} ({self.year})"
    
    class Meta:
        db_table = 'secretchild'
        verbose_name = "secretchild" 
        verbose_name_plural = "secretchildren"