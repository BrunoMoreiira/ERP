from rest_framework.exceptions import AuthenticationFailed, APIException
from accounts.models import User
from companies.models import Employee, Enterprise
from django.contrib.auth.hashers import check_password, make_password

class Authentication:
    def signin(self, email=None, password=None) -> User:
        exception_auth = AuthenticationFailed('Email e/ou senha incorreto(s)')
        user_exists = User.objects.filter(email=email).exists()

        if not user_exists:
            raise exception_auth
    
        user = User.objects.filter(email=email).first()
        
        if not check_password(password, user.password):
            raise exception_auth
        
        return user


    def signup(self, email, password, name, type_account='owner', company_id='False'):
        if not name or name == '':
            raise APIException('Nome é obrigatório')
        
        if not email or email == '':
            raise APIException('Email é obrigatório')
        
        if not password or password == '':
            raise APIException('Senha é obrigatória')
        
        if type_account == 'employee' and not company_id:
            raise APIException('Para cadastro de funcionário, é necessário informar a empresa')

        user = User
        if user.objects.filter(email=email).exists():
            raise APIException('Email já cadastrado, faça o Login para acessa-lo')
        
        password_hashed = make_password(password)

        created_user = user.objects.create(
            email=email,
            password=password_hashed,
            name=name,
            is_owner=0 if type_account == 'employee' else 1,
        )

        if type_account == 'owner':
            created_enterprise = Enterprise.objects.create(
                name='Nome da empresa',
                user_id=created_user.id     
            )
        if type_account == 'employee':
            Employee.objects.create(
                name='Nome do funcionário',
                user_id=created_user.id,
                enterprise_id=company_id or created_enterprise.id
            )

        return created_user