from .models import Employee


class LocalAuth:
    """class to Authenticate Custom user"""

    def authenticate(email, password):
        try:
            emp = Employee.objects.get(email=email)
            if emp is not None:
                if emp.password == password:
                    return emp
        except:
            return None