from .models import Employee
class CustomAuth():
    """class to Authenticate Custom user"""
    def authenticate(email, password):
        try:
            user=Employee.objects.get(email=email)
            if user is not None:
                if(user.password==password):
                    return user
        except:
            return 