from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from companies.models import Employee, Enterprise
from accounts.models import User_Groups, GroupPermission

class Base(APIView):
    def get_enterprise_user(self, user_id):
        enterprise = {
            "is_owner": False,
            "permissions": []
        }
        enterprise['is_owner'] = Enterprise.objects.filter(user_id=user_id).exists()

        if enterprise['is_owner']:
            return enterprise
        return None

    def get_employee_and_groups(self, user_id):
        employee = Employee.objects.filter(user_id=user_id).first()

        if not employee:
            raise APIException("Este usuário não é um funcionário")

        enterprise = {
            "is_owner": False,
            "permissions": []
        }

        groups = User_Groups.objects.filter(user_id=user_id).all()
        
        for g in groups:
            group = g.group 
            
            permissions = GroupPermission.objects.filter(group_id=group.id).all()

            for p in permissions:
                enterprise['permissions'].append({
                    "id": p.permission.id,
                    "label": p.permission.name,
                    "codename": p.permission.codename,
                })

        return enterprise
