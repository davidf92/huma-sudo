
import tkinter.tix as tix

win=None
top=None
bt=None
win2 = None
top2 = None
bt2 = None
widgets = (tix, win, top, bt, win2, top2, bt2)

def start(widgets):

    print("start")
    print(widgets)
    
    (tix, win, top, bt, win2, top2, bt2) = widgets

    win = tix.Tk()
    win.title("Test GUI with tix")
    top = tix.Frame(win, bg = "red")
    top.pack(fill="both", expand=True)
    bt = tix.Button(top, text="Ok", command=lambda f=top : evBt1(f))
    bt.pack(side="left", padx=5, pady=2)

##    win2 = tix.Tk()
##    win2.title("Test GUI #2 with tix")
##    top2 = tix.Frame(win2, bg = "blue")
##    top2.pack(fill="both", expand=True)
##    bt2 = tix.Button(top2, text="Ok", command=evBt2)
##    bt2.pack(side="top", padx=5, pady=2)

    widgets = (tix, win, top, bt, win2, top2, bt2)
    print(widgets)
    return widgets

def evBt1(frame):
    print("Ok in win 1")
    frame.quit()
    return

def evBt2(frame):
    print("Ok in win 2")
    frame.quit
    return

print("__name__ = " + str(__name__))

#exécution standalone ou dans le shell
if __name__ == "__main__":

    (tix, win, top, bt, win2, top2, bt2) = \
          start((tix, win, top, bt, win2, top2, bt2))
    tix.mainloop()
    win.destroy()

    print("The end")
    s = input("Tapez ENTREE pour terminer...")
    #exit()


