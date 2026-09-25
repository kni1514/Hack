import requests
import json
import re

output = ""

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'http://mitsims.in',
    'Referer': 'http://mitsims.in/gemsonline-student/getConsolidatedView.action'
}

session.get("http://mitsims.in/", headers=headers)

login_url = "http://mitsims.in/studentLogin/studentLogin.action?personType=student"

uname    = input("Enter Roll Number       : ")
password = input("Enter Password          : ")
who_am  =  input("Are You Student ? (Y/N) : ")[0].lower()
role = "student"
if who_am != 'y' :
    role="faculty"

login_payload = {
    "userId": uname,
    "password": password,
    "personType": role
}

login_headers = headers.copy()
login_headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

login_resp = session.post(login_url, data=login_payload, headers=login_headers)

if login_resp.status_code == 200:
    redirect_url = "http://mitsims.in/studentLogin/studentReDirect.action?personType=student"
    session.get(redirect_url, headers=login_headers)

    view_url = "http://mitsims.in/gemsonline-student/getConsolidatedView.action"
    session.get(view_url, headers=headers)

    dashboard_url = "http://mitsims.in/gemsonline-student/dashboard.action?actionType=scv&keyString=consolidate"

    payload = {
        "usn": uname,
        "actionType": "scv",
        "keyString": "consolidate",
        "req": "./student/exec.action?actionType=scv&keyString=consolidate"
    }

    data_resp = session.post(dashboard_url, json=payload, headers=headers)

    if data_resp.status_code == 400 or data_resp.status_code == 415:
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        simple_payload = {
            "usn": uname,
            "actionType": "scv",
            "keyString": "consolidate"
        }
        data_resp = session.post(dashboard_url, data=simple_payload, headers=headers)

    try:
        data = data_resp.json()
        output = json.dumps(data, indent=4)
    except Exception:
        output = data_resp.text
else:
    output = f"SERVER TO SLOW : {login_resp.status_code}"

blocks = re.findall(
    r"xtype\s*:\s*'fieldset'(.*?)(?=xtype\s*:\s*'fieldset'|$)",
    output,
    re.DOTALL
)

print("\nDEVELOPER :  Niranjan Kumar K")

print(f"\n{'COURSE':<10}{':':<2}{'PERCENTAGE'}")
print(f"{'------':<10}{'+':<2}{'----------'}\n")

p=[]

for block in blocks:
    code = re.search(
        r'font-size:12px">\s*([A-Z0-9]+)\s*</span>',
        block
    )

    att = re.search(
        r'color:[^;]+;\s*padding:\s*37px;">\s*([\d.]+)\s*</span>',
        block
    )

    if code and att:
        p.append(att.group(1))
        print(f"{code.group(1):<10}{':':<2}{att.group(1):<7}%")

s = 0
t = 0

for i in p :
    s = s + float(i)

t = s/len(p)

print(f"\nTOTAL PERCENTAGE = {t} %\n")
