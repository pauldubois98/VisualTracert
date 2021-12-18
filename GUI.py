import tkinter as tk



root = tk.Tk()
root.title("Visual tracert")
adress_entry = tk.Entry(root, width=60, justify='center')
adress_entry.pack(pady=2)

tracert_button = tk.Button(root, text='tracert')
tracert_button.pack()


root.mainloop()


