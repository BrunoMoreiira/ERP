from companies.views.base import Base
from companies.utils.permissions import GroupsPermission
from companies.utils.exceptions import RequiredFields
from companies.serializers import GroupsSerializer

from accounts.models import Group, GroupPermission

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.contrib.auth.models import Permission

class Groups(Base):
    permission_classes = [GroupsPermission]

    def get(self, request):
        """
        Recupera todos os grupos associados à empresa atual.

        Parâmetros:
        request (Request): O objeto de requisição contendo as informações do usuário.

        Retorna:
        Response: Uma resposta JSON contendo uma lista de grupos.
        """
        enterprise_id = self.get_enterprise_id(request.user.id)
        groups = Group.objects.filter(enterprise_id=enterprise_id).all()

        serializer = GroupsSerializer(groups, many=True)
        return Response({'groups': serializer.data})

    def post(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)
        
        name = request.data.get('name')
        permissions = request.data.get('permissions')

        if not name:
            raise RequiredFields
        
        created_group = Group.objects.create(
            name=name,
            enterprise_id=enterprise_id
        )
        
        if permissions and isinstance(permissions, str):
            permissions = permissions.split(',')

        if permissions and isinstance(permissions, list):
            try:
                for item in permissions:
                    try:
                        item = int(item.strip())
                    except ValueError:
                        raise ValueError("Permissões devem ser IDs inteiros")

                    permission_exists = Permission.objects.filter(id=item).exists()
                    if not permission_exists:
                        created_group.delete()
                        raise APIException(f'Você não possui a permissão {item}')
                    
                    if not GroupPermission.objects.filter(group_id=created_group.id, permission_id=item).exists():
                        GroupPermission.objects.create(
                            group_id=created_group.id,
                            permission_id=item
                        )
            except ValueError as e:
                created_group.delete()
                raise APIException(f"Envie as permissões no padrão correto: {str(e)}")
        
        else:
            created_group.delete()
            raise APIException("As permissões devem ser fornecidas como uma lista válida ou uma string separada por vírgulas.")
        
        return Response({"success": True})

class GroupDetail(Base):
    permission_classes = [GroupsPermission]
    
    def get(self, request, group_id):
        """
        Recupera os dados de um grupo específico associado à empresa atual.
    
        Parâmetros:
        request (Request): O objeto de requisição contendo as informações do usuário.
        group_id (int): O ID do grupo.
        
        Retorna:
        Response: Uma resposta JSON contendo os dados do grupo. 
        """
        enterprise_id = self.get_enterprise_id(request.user.id)
        self.get_group(group_id, enterprise_id)
        group = Group.objects.filter(id=group_id, enterprise_id=enterprise_id).first()

        serializer = GroupsSerializer(group)
        
        return Response({'group': serializer.data})
    
    def delete(self, request, group_id):
        """
        Remove um grupo específico associado à empresa atual.
        
        Parâmetros:
        request (Request): O objeto de requisição contendo as informações do usuário.
        group_id (int): O ID do grupo.
        
        Retorna:
        Response: Uma resposta JSON indicando sucesso ou falha da operação.
        """
        enterprise_id = self.get_enterprise_id(request.user.id)
        Group.objects.filter(id=group_id, enterprise_id=enterprise_id).delete()
        
        return Response({"success": True})
    
    def put(self, request, group_id):
        """
        Atualiza os dados de um grupo específico associado à empresa atual.
        
        Parâmetros:
        request (Request): O objeto de requisição contendo as informações do usuário e os dados do grupo.
        group_id (int): O ID do grupo.
        
        Retorna:
        Response: Uma resposta JSON indicando sucesso ou falha da operação.
        """
        enterprise_id = self.get_enterprise_id(request.user.id)
        self.get_group(group_id, enterprise_id)
        
        name = request.data.get('name')
        permissions = request.data.get('permissions')
        
        if name:
            Group.objects.filter(id=group_id).update(
                name=name
            )
        
        # Limpar permissões antigas
        GroupPermission.objects.filter(group_id=group_id).delete()
        
        # Se permissions for uma string, convertê-la para uma lista
        if permissions and isinstance(permissions, str):
            permissions = permissions.split(',')
        
        # Continuar com o processo, verificando se permissions é uma lista
        if permissions and isinstance(permissions, list):
            try:
                for item in permissions:
                    # Remover espaços em branco e converter para inteiro
                    try:
                        item = int(item.strip())
                    except ValueError:
                        raise ValueError("Permissões devem ser IDs inteiros")

                    permission_exists = Permission.objects.filter(id=item).exists()
                    if not permission_exists:
                        raise APIException(f'Você não possui a permissão {item}')
                    
                    if not GroupPermission.objects.filter(group_id=group_id, permission_id=item).exists():
                        GroupPermission.objects.create(
                            group_id=group_id,
                            permission_id=item
                        )
            except ValueError as e:
                raise APIException(f"Envie as permissões no padrão correto: {str(e)}")
        
        return Response({"success": True})