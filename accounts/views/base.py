from rest_framework.views import APIView
from companies.models import Enterprise


class Base(APIView):
    def get_enterprise_user(self,user_id):
        enterprise= {
            "is_owner": False,
            "permissions": []
        }
        enterprise['is_owner'] = Enterprise.objects.filter(user_id=user_id).exists()

        if enterprise['is_owner']:
            return enterprise
        
    # Permissions, Get Employee