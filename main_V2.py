import subprocess
import json

def set_role_user(sp,id_user,role):
    payload_json = '{{"principalId": "{}","resourceId": "{}","appRoleId": "{}"}}'.format(id_user,sp,role)

    subprocess.run(f"az rest -m post -u https://graph.microsoft.com/v1.0/servicePrincipals/{sp}/appRoleAssignments --headers \"Content-Type=application/json\" -b '{payload_json}'", shell=True)

def list_appRoleAssignments(user_id):
    var_command = """"(resourceDisplayName|id)": "\K[^"]*' | awk 'NR%2{ printf "%s = ", $0; next;}1"""
    subprocess.run(f"""az rest -m GET -u https://graph.microsoft.com/v1.0/users/{user_id}/appRoleAssignments | grep -Po '{var_command}' | grep {sigla_app}""", shell=True)

def delete_appRoleAssignments(user,assigned):
    subprocess.run(f"az rest -m DELETE -u https://graph.microsoft.com/v1.0/users/{user}/appRoleAssignments/{assigned}", shell=True)

while True:

    function_var2 = input("""
    [ SET ROLE PROGRAM ]

    Digite o numero da funções desejada:
    
    1) Inserir Perfil para usuário interno (Cosan)
    2) Inserir Perfil para usuário externo 
    3) Remover Perfil para usuário interno (Cosan)
    4) Remover Perfil para usuário externo

    """)
    
    user_ad = input('Insira o código do usuário: ').strip()
    sigla_app = input('Insira a sigla da aplicação: ').strip().upper()

    id_app_azure = subprocess.check_output(f"az ad app list --filter \"displayname eq \'{sigla_app}\'\" | jq .[].appId | sed \'s/^\"//\' | sed \'s/\"$//\'", shell=True).rstrip()
    id_app_azure = str(id_app_azure, 'utf-8')
    if id_app_azure == '':
        print('ERRO: Aplicação não encontrada')
        continue
    #print(id_app_azure)

    id_sp_app_azure=subprocess.check_output(f"az ad sp list --filter \"displayname eq \'{sigla_app}\'\" | jq .[].id | sed \'s/^\"//\' | sed \'s/\"$//\'", shell=True).rstrip()
    id_sp_app_azure = str(id_sp_app_azure, 'utf-8')
    if id_sp_app_azure == '':
        print('ERRO: Service principal da aplicação não encontrado')
        continue
    #print(id_sp_app_azure)

    if function_var2 == '1' or function_var2 == '3':
        id_user_azure=subprocess.check_output(f"az ad user list --upn {user_ad}_minhati.com.br#EXT#@ADRISQAS.onmicrosoft.com | jq .[].id | sed \'s/^\"//\' | sed \'s/\"$//\'", shell=True).rstrip()
        id_user_azure = str(id_user_azure, 'utf-8')
    else:
        id_user_azure=subprocess.check_output(f"az ad user list --upn {user_ad}@ADRISQAS.onmicrosoft.com | jq .[].id | sed \'s/^\"//\' | sed \'s/\"$//\'", shell=True).rstrip()
        id_user_azure = str(id_user_azure, 'utf-8')
    #print(id_user_azure)

    if id_user_azure == '':
        print('ERRO: Usuário não encontrar')
        continue
    
    if function_var2 == '3' or function_var2 == '4':
        
        assign_list_delete = []
        another_role = 'y'

        list_appRoleAssignments(id_user_azure)
        while another_role == 'y':
            role_delete = input('Selecione o ID da role que vc deseja excluir: ')
            assign_list_delete.append(role_delete)
            another_role = input('Deseja selecionar outra role para excluir? (n/y) ').strip().lower()
        
        for i in assign_list_delete:
            delete_appRoleAssignments(id_user_azure,i)
    
    else:
        roles = subprocess.check_output(f"az ad app list --filter \"displayname eq \'{sigla_app}'\" |jq .[].appRoles", shell=True).rstrip()
        roles = str(roles, 'utf-8')
        data_json  = json.loads(roles)

        roles_app = []

        for i in data_json:
            data = { 'Role_name': i['displayName'], 'ID_role': i['id'] }
            roles_app.append(data)

        count = 0
        for i in roles_app:
            print(f'{count}: {i}')
            count += 1

        another_role = 'y'
        roles_list = []

        while another_role == 'y':
            selected_role = int(input(f'Digite o numero da linha que contem a role que vc deseja atribuir ao usuário {user_ad} para a aplicação {sigla_app}? '))
            roles_list.append(selected_role)
            another_role = input('Deseja selecionar outra role para ser atribuida ao usuário? (n/y) ').strip().lower()

        for i in roles_list:
            id_role_set = roles_app[i]['ID_role']
            print(id_role_set)
            set_role_user(id_sp_app_azure,id_user_azure,id_role_set)
            print('----------------------------------------------------------------')