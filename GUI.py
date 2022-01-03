import tkinter as tk
import requests
import json
import numpy as np
import plotly.express as px
import threading
import os


def finished(filename):
    f = open(filename, 'r')
    ls =  f.readlines()
    if "Itin‚raire d‚termin‚.\n" in ls:
        return True
    else:
        return False

def get_ips(filename):
    f = open(filename, 'r')
    ls =  f.readlines()
    if len(ls)<5:
        return []
    ips = []
    i=4
    l = ls[i]
    while i+1<len(ls) and l!='\n' and l!='':
        
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
    full_coords = []
    for ip in ips:
        coord = get_coord(ip)
        if not coord is None:
            coords.append(coord)
            print(ip, coord)
        full_coords.append(coord)

    np_coords = np.array(coords)
    return np_coords, full_coords

def plot(np_coords):
    lats = np_coords[:,0]
    lons = np_coords[:,1]
    # fig = px.line_geo(lat=lats, lon=lons)
    fig = px.line_geo(lat=lats, lon=lons, projection="orthographic")
    fig.show()
    fig.write_image("fig.png")

def tracert():
    global root, adress_entry, thread, filename
    if adress_entry.get()=='_':
        filename="tracert.txt"
        adress_entry.delete(0, tk.END)
        root.after(1000, update)
    else:
        filename="tracert.txt"
        thread = TracertThread(adress_entry.get(), filename).start()
        adress_entry.delete(0, tk.END)
        root.after(1000, update)

def update():
    global root, ip_list, thread, filename, ips, np_coords, full_coords
    new_ips = get_ips(filename)
    if len(new_ips)>len(ips):
        ip_list.config(text='\n'.join(ips)+'\n...')
    if finished(filename):
        np_coords, full_coords = get_coords(ips)
        txt = ""
        i = 0
        print(ips)
        print(np_coords)
        while i<len(ips):
            txt += ips[i]
            txt += ' - '
            txt += str(full_coords[i])
            txt += '\n'
            i += 1
        ip_list.config(text=txt[:-1])
        plot(np_coords)
    else:
        root.after(1000, update)


class TracertThread(threading.Thread):
    def __init__(self, adress, filename="tracert.txt"):
        threading.Thread.__init__(self)
        self.adress = adress
        self.filename = filename

    def run(self):
        global image_label
        cmd = 'tracert '+self.adress+' > ' + self.filename
        print(cmd)
        os.system(cmd)
        print('root determined')
        # ips = get_ips(self.filename)
        # np_coords, full_coords = get_coords(ips)
        # plot(np_coords)


thread = None
filename = None
ips = None
np_coords = None
full_coords = None
root = tk.Tk()
root.title("Visual tracert")
adress_entry = tk.Entry(root, width=60, justify='center')
adress_entry.pack(pady=2)
ip_list = tk.Label(root, text="")
ip_list.pack()
tracert_button = tk.Button(root, text='tracert', command=tracert)
tracert_button.pack()

root.mainloop()
