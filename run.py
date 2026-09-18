from requests import post
from sys import argv

languages = ['python', 'cpp', 'c', 'java', 'javascript', 'typescript', 'go', 'rust', 'csharp', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'perl', 'bash', 'haskell', 'lua', 'pascal', 'sql']

def help():
    print("Usage     : execute <lang> file_name.ext")
    print("Languages : ",languages)

url = "https://playground.nextleet.com/api/compiler/execute"

def run(file_name,lang,stdin):
    with open(file_name) as f :
        code = f.read()
    payload = {"sourceCode":code,"language":lang,"stdin":stdin}
    response = post(url,json=payload)
    return response.json()

def display(output):
    if output["stdout"] != None:
        print("\nOUTPUT : \n")
        print(output["stdout"])
    if output["stderr"]!=None :
        print("\nERROR : \n")
        print(output["stderr"])
    if output["compile_output"]!=None :
        print("\nCOMPILED OUTPUT :\n")
        print(output["compile_output"])


if len(argv)<=2:
    help()
    exit(0)
elif argv[1] not in languages :
    print("please use language from : ",languages)
    exit(0)
else :
    try :
        with open(argv[2]) as f :
            pass
    except FileNotFoundError:
        print("please use proper file name !")
        exit(0)

stdin = ""

for value in argv[3:]:
    stdin = stdin + value + "\n"

display(run(argv[2],argv[1],stdin))
