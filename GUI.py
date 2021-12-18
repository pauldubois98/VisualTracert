import tkinter as tk
import requests
import json


def get_ips(filename):
    f = open(filename, 'r')
    ls =  f.readlines()
    ips = []
    i=4
    l = ls[i]
    while i<len(ls) and l!='\n' and l!='':
        
        if '[' in l and '[' in l:
            a = l.find('[')
            b = l.find(']')
            ips.append(l[a+1:b])
        else:
            ips.append(l[33:].rstrip())
        i+=1
        l = ls[i]
    f.close()
    return ips

def get_coord(ip):
    r = requests.get('http://ip-api.com/json/'+ip)
    js = json.loads(r.text)
    try:
        return (js['lat'], js['lon'])
    except:
        return None



root = tk.Tk()
root.title("Visual tracert")
adress_entry = tk.Entry(root, width=60, justify='center')
adress_entry.pack(pady=2)

tracert_button = tk.Button(root, text='tracert')
tracert_button.pack()


root.mainloop()


