import tkinter as tk
import requests
import json
import numpy as np
import plotly.express as px
import threading
import os

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

def get_coords(ips):
    coords = []
    for ip in ips:
        coord = get_coord(ip)
        if not coord is None:
            coords.append(coord)
            print(ip, coord)
    np_coords = np.array(coords)
    return np_coords

def plot(np_coords):
    lats = np_coords[:,0]
    lons = np_coords[:,1]
    # fig = px.line_geo(lat=lats, lon=lons)
    fig = px.line_geo(lat=lats, lon=lons, projection="orthographic")
    fig.show()

def tracert():
    global adress_entry
    TracertThread(adress_entry.get()).start()
    adress_entry.delete(0, tk.END)

class TracertThread(threading.Thread):
    def __init__(self, adress):
        threading.Thread.__init__(self)
        self.adress = adress

    def run(self):
        global image_label
        cmd = 'tracert '+self.adress+' > data/d_'+str(threading.get_native_id())+'.txt'
        print(cmd)
        os.system(cmd)
        print('root determined')
        filename = 'data/d_'+str(threading.get_native_id())+'.txt'
        ips = get_ips(filename)
        np_coords = get_coords(ips)
        plot(np_coords)

root = tk.Tk()
root.title("Visual tracert")
adress_entry = tk.Entry(root, width=60, justify='center')
adress_entry.pack(pady=2)

tracert_button = tk.Button(root, text='tracert', command=tracert)
tracert_button.pack()

root.mainloop()
