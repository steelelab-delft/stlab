import tkinter as tk
from tkinter import messagebox


class popup_warning():
    def __init__(self, dev_id='Instrument XYZ'):
        self.reset = True
        self.root = tk.Tk()  # create window

        self.canvas1 = tk.Canvas(self.root, width=500, height=350)
        self.background_image = tk.PhotoImage(
            file='C:\\libs\\stlab\\utils\\Gary-Steele-web.gif')
        self.canvas1.create_image(400, 300, image=self.background_image)
        self.canvas1.create_text(
            300,
            100,
            text=
            '\n##################################\nWarning! Reset instrument set to false. \nYou should reset this instrument:\n'
            + dev_id + '##################################',
            font='bold')
        self.canvas1.config(background='red')
        self.canvas1.pack()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            print('Aborting script')
            self.root.destroy()
            raise SystemExit('You closed the window, which aborted the script')

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        button1 = tk.Button(
            self.root,
            text='Continue with caution',
            command=self.ExitApplication)
        self.canvas1.create_window(97, 270, window=button1)
        self.root.mainloop()
        return self.reset

    def ExitApplication(self):
        MsgBox = tk.messagebox.askquestion(
            'Continue with caution',
            'Warning! No instrument reset found. Do you want to reset the instrument?',
            icon='warning')
        if MsgBox == 'yes':
            printmsg = 'Resetting the instrument and continuing...'
            tk.messagebox.showinfo('Resetting the instrument', printmsg)
            print(printmsg)
            self.reset = True
        else:
            MsgBox = tk.messagebox.askquestion(
                '??? Are you sure ???',
                'Do you really not want to reset the instrument?',
                icon='warning')
            if MsgBox == 'yes':
                printmsg = 'The script will continue without reset at your own risk...'
                tk.messagebox.showinfo('Continue at own risk', printmsg)
                print(printmsg)
                self.reset = False
            else:
                printmsg = 'Resetting the instrument and continuing...'
                tk.messagebox.showinfo('Resetting the instrument', printmsg)
                print(printmsg)
                self.reset = True

        self.root.destroy()


if __name__ == "__main__":
    result = popup_warning()
    print('reset:', result)
