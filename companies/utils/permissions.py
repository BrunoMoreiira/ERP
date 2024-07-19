from rest_framework import permissions
from accounts.models import User_Groups, GroupPermission
from django.contrib.auth.models import Permission

def check_permissions(user, method, permissions_to):
    if not user.is_authenticated:
        return False

    if user.is_owner:
        return True
    
    required_permission = 'view_'+permissions_to
    if method =='POST':
        required_permission = 'add_'+permissions_to
    elif method =='PUT':
        required_permission = 'change_'+permissions_to
    elif method =='DELETE':
        required_permission = 'delete_'+permissions_to

    groups = User_Groups.objects.values('group_id').filter(user_id=user.id).all()

    for group in groups:
        permissions = Permission.objects.values('permission_id').filter(group_id=group['group_id']).all()

        for permission in permissions:
            if Permission.objects.filter(id=permission['permission_id'], codename=required_permission).exists():
                return True

class employeesPermission (permissions.BasePermission):
    message = 'Acesso negado: Você não possui as permissões necessárias para gerenciar os funcionários desta empresa. Por favor, entre em contato com o administrador do sistema para obter mais informações.'

    def has_permission(self, request, _view):
        return check_permissions(request.user, request.method, permissions_to='employee')
    

class GroupsPermission (permissions.BasePermission):
    message = 'Acesso negado: Você não possui as permissões necessárias para gerenciar os grupos. Por favor, entre em contato com o administrador do sistema para obter mais informações.'

    def has_permission(self, request, _view):
        return check_permissions(request.user, request.method, permissions_to='group')
    
class GroupsPermissionPermission (permissions.BasePermission):
    message = 'Acesso negado: Você não possui as permissões necessárias para gerenciar as permissões dos grupos. Por favor, entre em contato com o administrador do sistema para obter mais informações.'

    def has_permission(self, request, _view):
        return check_permissions(request.user, request.method, permissions_to='permission')
    
class TaskPermission (permissions.BasePermission):
    message = 'Acesso negado: Você não possui as permissões necessárias para gerenciar as tarefas. Por favor, entre em contato com o administrador do sistema para obter mais informações.'

    def has_permission(self, request, _view):
        return check_permissions(request.user, request.method, permissions_to='task')
