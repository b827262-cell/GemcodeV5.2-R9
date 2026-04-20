import tkinter as tk
import time

class DigitalClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Clock")
        self.resizable(False, False)
        self.configure(bg='black')
        
        self.time_label = tk.Label(
            self,
            font=('Helvetica', 48, 'bold'),
            background='black',
            foreground='cyan'
        )
        self.time_label.pack(padx=30, pady=20)
        
        self.update_clock()

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        self.time_label.config(text=current_time)
        self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = DigitalClock()
    app.mainloop()
