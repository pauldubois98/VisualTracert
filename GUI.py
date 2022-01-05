import tkinter as tk
import requests
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import threading
import os
import time
from PIL import ImageTk,Image
from requests.sessions import ContentDecodingError  


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

def plot_img(np_coords, finished=True, color=None):
    lats = np_coords[:,0]
    lons = np_coords[:,1]
    n = len(lats)-1
    fig = go.Figure()
    for i in range(n):
        if color is None:
            a = 2*np.pi*i/n
            r = int(255*((np.cos(a)+1)/2))
            g = int(255*((np.cos(a+2*np.pi/3)+1)/2))
            b = int(255*((np.cos(a+4*np.pi/3)+1)/2))
            c = 'rgb('+str(r)+','+str(g)+','+str(b)+')'
        else:
            c = color
        fig.add_trace(go.Scattergeo(lat=[lats[i], lats[i+1]], lon=[lons[i], lons[i+1]], \
                                    mode = 'lines', line = dict(width = 2, color = c) ))
    fig.add_trace(go.Scattergeo(lat=[lats[0]],lon=[lons[0]]))
    if finished:
        fig.add_trace(go.Scattergeo(lat=[lats[-1]],lon=[lons[-1]]))
    fig.write_image("fig.png", scale=1)
    ### for higher resolution:
    # fig.write_image("fig.png", scale=2)
    ### for web display:
    # fig.show()


def tracert():
    global root, tracert_button, adress_entry, thread, filename, ips, np_coords, full_coords, coords
    if adress_entry.get()=='_':
        #quicker: use old tracert data
        filename="tracert.txt"
        adress_entry.delete(0, tk.END)
        root.after(1000, update)
    else:
        website = adress_entry.get()
        try:
            response = requests.get("http://"+website)
        except:
            adress_entry.config(bg='red')
        else:
            if response.status_code == 200:
                #kill old thread if needed
                if thread is None:
                    pass
                else:
                    thread._stop()
                    thread = None
                    filename = None
                    ips = []
                    coords = []
                    np_coords = np.array([[1,1]])
                    full_coords = []
                #do the job
                adress_entry.config(bg='white')
                filename="tracert.txt"
                thread = TracertThread(website, filename).start()
                adress_entry.delete(0, tk.END)
                ip_list.config(text='...')
                tracert_button.config(state='disable')
                root.after(1000, update)
            else:
                adress_entry.config(bg='red')
            
        

def update():
    global root, tracert_button, ip_list, map_show, thread, filename, ips, coords, np_coords, full_coords, img
    new_ips = get_ips(filename)
    if len(new_ips)>len(ips):
        i = len(ips)
        while i<len(new_ips):
            ip = new_ips[i]
            coord = get_coord(ip)
            full_coords.append(coord)
            if not coord is None:
                coords.append(coord)
            i += 1
        np_coords = np.array(coords)
        ips = new_ips

        txt = ""
        i = 0
        while i<len(ips):
            txt += ips[i]
            txt += ' - '
            txt += str(full_coords[i])
            txt += '\n'
            i += 1
        ip_list.config(text=txt+'...')
        plot_img(np_coords, False)
        time.sleep(0.1)
        img = ImageTk.PhotoImage(Image.open("fig.png"))      
        map_show.create_image(-76,-128, anchor=tk.NW, image=img)
    if finished(filename):
        np_coords, full_coords = get_coords(ips)
        txt = ""
        i = 0
        while i<len(ips):
            txt += ips[i]
            txt += ' - '
            txt += str(full_coords[i])
            txt += '\n'
            i += 1
        ip_list.config(text=txt[:-1])
        plot_img(np_coords)
        time.sleep(1)
        img = ImageTk.PhotoImage(Image.open("fig.png"))      
        map_show.create_image(-76,-128, anchor=tk.NW, image=img)
        tracert_button.config(state='normal')
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
        # plot_web(np_coords)


thread = None
filename = None
ips = []
coords = []
np_coords = np.array([[1,1]])
full_coords = []

root = tk.Tk()
root.title("Visual tracert")

adress_entry = tk.Entry(root, width=60, justify='center')
adress_entry.pack(pady=2)

ip_list = tk.Label(root, text="")
ip_list.pack()

tracert_button = tk.Button(root, text='tracert', command=tracert)
tracert_button.pack()

map_show = tk.Canvas(root, width = 513, height = 261)
map_show.pack()
img = ImageTk.PhotoImage(Image.open("fig0.png"))  
map_show.create_image(-76,-128, anchor=tk.NW, image=img)

root.mainloop()
