#############
### Import`s ###`
############

import os
import subprocess
import json
import requests

import sys
from colorama import init, Fore
from time import sleep
#############
### Tempory ###
############


projects_file = './src/json/projects.json'
installed_projects_dir = './src/installed_projects'


CURRENT_VERSION = "1.0.0"
GITHUB_API_URL = "https://api.github.com/repos/d3rrk1a/d3rrk1a_hub/releases/latest"

############
### Creator ###
############

#
#   ,._., ._                          .:'/*/'`:,·:~·–:.,               .:'/*/'`:,·:~·–:.,                  _                   _                 ,.-:~:-.            
#  /::::::::::'/:/:~-.,               /::/:/:::/:::;::::::/`':.,'        /::/:/:::/:::;::::::/`':.,'        .:'´::::`';           ,·/::::`;'           /':::::::::'`,          
# /:-·:;:-·~·';/:::::::::`·-.       /·*'`·´¯'`^·-~·:–-'::;:::'`;     /·*'`·´¯'`^·-~·:–-'::;:::'`;      /:::::::::'¦      ,:´::/::::::/'‚         /;:-·~·-:;':::',         
# ';           '`~-:;:::::::::'`,    '\                       '`;::'i‘   '\                       '`;::'i‘   /·'´ '¯ `';:;| .:´:::;'´ ¯'`:;/  ‘       ,'´          '`:;::`,       
#  ',.                 '`·-:;:::::'i'‘   '`;        ,– .,        'i:'/      '`;        ,– .,        'i:'/    ;         '¦:/:::::'´       / ‘         /                `;::\      
#    `'i      ,_            '`;:::'¦‘     i       i':/:::';       ;/'         i       i':/:::';       ;/'     i         '|/:::·´      .·'´          ,'                   '`,::;    
#     'i      ;::/`:,          i'::/      i       i/:·'´       ,:''           i       i/:·'´       ,:''       ';         '·´   ,.-:'´:`;.          i'       ,';´'`;         '\:::', ‘
#    _;     ;:/;;;;:';        ¦'/        '; '    ,:,     ~;'´:::'`:,        '; '    ,:,     ~;'´:::'`:,    ';         ;',    `;·;:::::'`,     ,'        ;' /´:`';         ';:::'i‘
#   /::';   ,':/::::::;'       ,´         'i      i:/\       `;::::/:'`;'     'i      i:/\       `;::::/:'`;'  ';        ;';'\      '`;:::::'`,   ;        ;/:;::;:';         ',:::;
#,/-:;_i  ,'/::::;·´        ,'´           ;     ;/   \       '`:/::::/'      ;     ;/   \       '`:/::::/'   ';      ';:/  '\       '`;:::::';'i        '´        `'         'i::'/
#'`·.     `'¯¯     '   , ·'´              ';   ,'       \         '`;/'       ';   ,'       \         '`;/'     ';     ;/     ',        '`;:::/¦       '/`' *^~-·'´\         ';'/'‚
#    `' ~·- .,. -·~ ´                    `'*´          '`~·-·^'´           `'*´          '`~·-·^'´         \   '/        '`·,      _';/'‚'`., .·´              `·.,_,.·´  ‚
#           '                                                                                                 `'´              `'*'´¯                                       
#
#



# Проверка, существует ли директория для установленных проектов
os.makedirs(installed_projects_dir, exist_ok=True)

############
### JSON`S ###
###########

def load_projects():
    if not os.path.exists(projects_file):
        print("Файл с проектами не найден.")
        return []
    
    with open(projects_file, 'r') as f:
        return json.load(f)

# Сохранение проектов в JSON-файл
def save_projects(projects):
    with open(projects_file, 'w') as f:
        json.dump(projects, f, indent=4)

# Вывод доступных проектов
def view_available_projects():
    projects = load_projects()
    print("\nДоступные проекты:")
    for i, project in enumerate(projects, start=1):
        print(f"{i}) {project['name']} - {project['description']} (Repo: {project['repo']}, Latest Version: {project['version']})")

#############
### PROJECT ###
############

def install_project(index):
    projects = load_projects()
    if index < 1 or index > len(projects):
        print("Неверный номер проекта.")
        return
    
    project = projects[index - 1]
    repo = project['repo']
    project_name = project['name']
    
    print(f"Установка {project_name} из репозитория {repo}...")
    project_path = os.path.join(installed_projects_dir, project_name)

    # Проверяем, установлен ли проект
    if os.path.exists(project_path):
        print(f"{project_name} уже установлен.")
        return
    
    subprocess.run(['git', 'clone', repo, project_path])
    project['installed_version'] = project['version']  # Устанавливаем текущую версию
    save_projects(projects)
    print(f"{project_name} успешно установлен!")

# Обновление установленного проекта
def update_installed_project(project_name):
    project_path = os.path.join(installed_projects_dir, project_name)
    projects = load_projects()

    if not os.path.exists(project_path):
        print("Проект не найден.")
        return
    
    project = next((p for p in projects if p['name'] == project_name), None)
    if not project:
        print("Проект не найден.")
        return

    # Переход в директорию проекта
    os.chdir(project_path)
    print(f"Обновление {project_name}...")
    subprocess.run(['git', 'pull'])  # Обновляем проект из репозитория
    project['installed_version'] = project['version']  # Обновляем установленную версию
    save_projects(projects)
    print(f"{project_name} успешно обновлён!")

# Удаление установленного проекта
def remove_installed_project(project_name):
    project_path = os.path.join(installed_projects_dir, project_name)
    if os.path.exists(project_path):
        subprocess.run(['rm', '-rf', project_path])
        print(f"{project_name} успешно удалён!")
    else:
        print("Проект не найден.")


#################
### Check Update ####
#################


# Проверка обновлений для хаба
def check_for_hub_updates():
    print("Проверка обновлений хаба...")

    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()  # Проверка на ошибки HTTP

        latest_release = response.json()
        latest_version = latest_release["tag_name"]  # Получаем последнюю версию
        release_notes = latest_release["body"]  # Получаем заметки о релизе

        if latest_version != CURRENT_VERSION:
            print(f"Доступно обновление: {latest_version}")
            print(f"Заметки к релизу:\n{release_notes}")
            update = input("Хотите обновить хаб до последней версии? (да/нет): ").strip().lower()
            if update == "да":
                # Логика для обновления хаба
                print("Обновление хаба...")  # Здесь добавьте код для обновления
                # Пример: subprocess.run(['git', 'pull']) для обновления локального репозитория
            else:
                print("Обновление отменено.")
        else:
            print("У вас последняя версия хаба.")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке обновлений: {e}")


# Вывод установленных проектов
def view_installed_projects():
    print("\nУстановленные проекты:")
    installed_projects = os.listdir(installed_projects_dir)
    if not installed_projects:
        print("Нет установленных проектов.")
        return

    for project_name in installed_projects:
        project_path = os.path.join(installed_projects_dir, project_name)
        if os.path.isdir(project_path):
            # Пытаемся получить установленную версию из projects.json
            projects = load_projects()
            project = next((p for p in projects if p['name'] == project_name), None)
            installed_version = project['installed_version'] if project else "Неизвестная версия"
            print(f"{project_name} - Установленная версия: {installed_version}")

##########
### DEF ###
#########

init(autoreset=True)



def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды '{command}': {e}")
        exit(1)

def cls():
    run_command("clear")
    print_ascii()

def start_menu():
    cls()
    sleep(5)
    run_command("clear")
    print_help()


def hel():
    run_command("clear")
    print_help()

def return_menu():
    sleep(5)
    hel()
    
###########
### PRINT ###
###########


def print_ascii():
    print(Fore.LIGHTRED_EX + """
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⡤⠤⠤⠤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠉⠛⢦⣤⠶⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣴⠞⢋⡽⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⠀⠀⠙⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⠟⠁⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡀⠀⠀⠉⠓⠦⣤⣤⣤⣤⣤⣤⣤⣄⣀⠀⠀⠀
⠀⠀⠀⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣷⡄⠀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣆⠀
⠀⠀⣠⠞⠁⠀⠀⣀⣠⣏⡀⠀⢠⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠿⡃⠀⠀⠄⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡆         d3rrk1a_Hub
⢀⡞⠁⠀⣠⠶⠛⠉⠉⠉⠙⢦⡸⣿⡿⠀⠀⠀⡄⢀⣀⣀⡶⠀⠀⠀⢀⡄⣀⠀⣢⠟⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠃        creator: ♡𝔡3𝔯𝔯𝔨1𝔞♡
⡞⠀⠀⠸⠁⠀⠀⠀⠀⠀⠀⠀⢳⢀⣠⠀⠀⠀⠉⠉⠀⠀⣀⠀⠀⠀⢀⣠⡴⠞⠁⠀⠀⠈⠓⠦⣄⣀⠀⠀⠀⠀⣀⣤⠞⠁⠀                                     
⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⠁⠀⢀⣀⣀⡴⠋⢻⡉⠙⠾⡟⢿⣅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠛⠉⠉⠀⠀⠀⠀
⠘⣦⡀⠀⠀⠀⠀⠀⠀⣀⣤⠞⢉⣹⣯⣍⣿⠉⠟⠀⠀⣸⠳⣄⡀⠀⠀⠙⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠙⠒⠒⠒⠒⠒⠚⠋⠁⠀⡴⠋⢀⡀⢠⡇⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⢀⡾⠋⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⡀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⢠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣇⠀⠀⠉⠋⠻⣄⠀⠀⠀⠀⠀⣀⣠⣴⠞⠋⠳⠶⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠦⢤⠤⠶⠋⠙⠳⣆⣀⣈⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """)


def print_help():
    print(Fore.LIGHTMAGENTA_EX + """
        \n  
                      ╔═════════════════════════════╗
                      ║  d3rrk1a Hub                ║
                      ╠═════════════════════════════╣
                      ║ 1) View Available Projects  ║
                      ║ 2) Install Project          ║
                      ║ 3) Remove Installed Project ║
                      ║ 4) Update Installed Project ║
                      ║ 5) Check for Hub Updates    ║
                      ║ 6) View Installed Projects  ║
                      ║ q) Exit                     ║
                      ╚═════════════════════════════╝
          """)





###########
### Main ###
##########


# Основная функция меню
def main():
    start_menu()
    while True:

        choice = input("")

        if choice == '1':
            view_available_projects()
            return_menu()
        elif choice == '2':
            view_available_projects()
            index = int(input("Введите номер проекта для установки: "))
            install_project(index)
        elif choice == '3':
            project_name = input("Введите имя установленного проекта для удаления: ")
            remove_installed_project(project_name)
        elif choice == '4':
            project_name = input("Введите имя установленного проекта для обновления: ")
            update_installed_project(project_name)
        elif choice == '5':
            check_for_hub_updates()
        elif choice == '6':
            view_installed_projects()
            return_menu()
        elif choice == 'q':
            run_command("clear")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == '__main__':
    main()
