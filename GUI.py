from typing import Tuple
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import tkinter
from tkinter import messagebox
from PIL import ImageTk, Image


class GUI(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__()
        container = tkinter.Frame(self)
        self.wm_title('Lap Data GUI')
        # container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = MainPage(container, self)
        self.frames[MainPage] = frame
        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        label = tkinter.Label(self, text="Lap Data")
        label.pack()
        self.root = controller
        self.root.resizable(False, False)

        self.root.columnconfigure(tuple(range(2)), weight=1)
        self.root.columnconfigure(2, weight=3)
        self.root.rowconfigure(tuple(range(24)), weight=1)

        default_font = ("Tahoma", 12)

        black = '#131313'
        blue = '#00a0de'
        white = '#ffffff'

        self.root.configure(background=black)
        self.time, self.distance, self.power = import_tdp_data('Data.txt')
        self.energy = np.zeros(len(self.power))
        self.total_energy = np.zeros(len(self.power))
        self.energy_recovered = np.zeros(len(self.power))
        self.energy_deployed = np.zeros(len(self.power))
        self.xx = 0.75
        self.energy_calculations()
        self.max_recovered = tkinter.StringVar(self.root, str(int(np.abs(np.min(self.energy_recovered)))))
        self.max_deployed = tkinter.StringVar(self.root, str(int(np.max(self.energy_deployed))))
        self.max_net = tkinter.StringVar(self.root, str(int(np.max(self.total_energy))))

        self.fig = Figure(figsize=(7, 4), dpi=70)
        self.fig2 = Figure(figsize=(7, 4.5), dpi=70)
        self.fig3 = Figure(figsize=(5, 4), dpi=70)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.root)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.root)

        self.x_axis_variable = tkinter.StringVar(name='x')
        self.x_axis_variable.set("Time (s)")

        self.y_axis_variable = tkinter.StringVar(name='y')
        self.y_axis_variable.set("Power (kW)")

        self.x_axis_menu = tkinter.OptionMenu(self.root, self.x_axis_variable, "Time (s)", "Distance (m)", "Power (kW)")
        self.x_axis_menu.config(bg=blue, font=default_font, fg=white)
        x_menu = self.root.nametowidget(self.x_axis_menu.menuname)
        x_menu.config(font=default_font, bg=blue, fg=white)
        self.y_axis_menu = tkinter.OptionMenu(self.root, self.y_axis_variable, "Time (s)", "Distance (m)", "Power (kW)")
        self.y_axis_menu.config(bg=blue, font=default_font, fg=white)
        y_menu = self.root.nametowidget(self.y_axis_menu.menuname)
        y_menu.config(font=default_font, bg=blue, fg=white)

        self.x_axis_variable.trace('w', self.update_plot1)
        self.y_axis_variable.trace('w', self.update_plot1)

        self.update_plot1(0, 0, 0)
        self.update_plot2()
        self.update_plot3()

        self.header = tkinter.Label(self.root, text="LAP DATA", font=("Tahoma", 20, "bold"), bg=black, fg=white)
        self.wae_img = ImageTk.PhotoImage(Image.open("wae logo.png"))
        self.wae_label = tkinter.Label(self.root, image=self.wae_img)

        xx_param_label = tkinter.Label(self.root, text="Parameter XX", font=default_font, bg=black, fg=white)
        self.xx_param_entry = tkinter.Entry(self.root, cursor='xterm', width=5, justify='center', font=default_font, bg=blue, fg=white)
        self.xx_param_entry.insert('end', 0.75)
        self.xx_param_entry.bind('<Return>', self.enter_xx)

        self.max_recovered_label = tkinter.Label(self.root, textvariable=self.max_recovered, font=default_font, fg=white)
        self.max_recovered_label['bg'] = blue
        self.max_recovered_header = tkinter.Label(self.root, text="Maximum Energy Recovered (kJ):", font=default_font, bg=black, fg=white)

        self.max_deployed_label = tkinter.Label(self.root, textvariable=self.max_deployed, font=default_font, bg=blue, fg=white)
        self.max_deployed_header = tkinter.Label(self.root, text="Maximum Energy Deployed (kJ):", font=default_font, bg=black, fg=white)

        self.max_net_label = tkinter.Label(self.root, textvariable=self.max_net, font=default_font, bg=blue, fg=white)
        self.max_net_header = tkinter.Label(self.root, text="Maximum Net Energy (kJ):", font=default_font, bg=black, fg=white)

        self.quit_button = tkinter.Button(master=self.root, text="Quit", command=self.root.quit, font=default_font)

        self.header.grid(row=5, column=2)
        self.wae_label.grid(row=4, column=2, sticky='ne', padx=10)
        self.quit_button.grid(row=23, column=3)
        self.x_axis_menu.grid(row=9, column=1)
        self.y_axis_menu.grid(row=6, column=0)
        xx_param_label.grid(row=22, column=2)
        self.xx_param_entry.grid(row=23, column=2)
        self.max_recovered_header.grid(row=16, column=2)
        self.max_recovered_label.grid(row=17, column=2)
        self.max_deployed_header.grid(row=18, column=2)
        self.max_deployed_label.grid(row=19, column=2)
        self.max_net_header.grid(row=20, column=2)
        self.max_net_label.grid(row=21, column=2)
        self.canvas.get_tk_widget().grid(row=3, column=1, rowspan=6, pady=5)
        self.canvas2.get_tk_widget().grid(row=10, column=1, rowspan=16, padx=5, pady=5)
        self.canvas3.get_tk_widget().grid(row=7, column=2, rowspan=6, columnspan=3, padx=10)

    def update_plot1(self, n, m, x):
        x_axis = self.time
        y_axis = self.power
        if self.x_axis_variable.get() == "Distance (m)":
            x_axis = self.distance
        elif self.x_axis_variable.get() == "Power (kW)":
            x_axis = self.power
        if self.y_axis_variable.get() == "Time (s)":
            y_axis = self.time
        elif self.y_axis_variable.get() == "Distance (m)":
            y_axis = self.distance
        self.fig.clf()
        ax1 = self.fig.add_subplot()
        ax1.plot(x_axis, y_axis)
        ax1.set_xlabel(self.x_axis_variable.get())
        ax1.set_ylabel(self.y_axis_variable.get())
        self.canvas.draw()

    def update_plot2(self):
        self.fig2.clf()
        ax2 = self.fig2.add_subplot()
        ax2.plot(self.distance, self.energy_recovered, label='Energy Recovered')
        ax2.plot(self.distance, self.energy_deployed, label='Energy Deployed')
        ax2.plot(self.distance, self.total_energy, label='Net Energy')
        ax2.set_xlabel("Distance (m)")
        ax2.set_ylabel("Energy (kJ)")
        self.fig2.suptitle("Energy vs. Distance")
        ax2.legend()
        self.canvas2.draw()

    def update_plot3(self):
        self.fig3.clf()
        ax3 = self.fig3.add_subplot(projection='3d')
        ax3.scatter(self.distance, self.time, self.power)
        ax3.set_xlabel('Distance (m)')
        ax3.set_ylabel('Time (s)')
        ax3.set_zlabel('Power (kW)')
        self.fig3.suptitle("Energy vs. Distance")
        ax3.legend()
        self.canvas3.draw()

    def energy_calculations(self):
        self.energy[0] = self.power[0] * self.time[0]
        self.total_energy[0] = self.energy[0]
        if self.energy[0] < 0:
            self.energy_recovered[0] = self.energy[0]
        else:
            self.energy_deployed[0] = self.energy[0]

        for i in range(1, len(self.power)):
            self.energy[i] = (self.power[i] + self.power[i - 1]) * (2 * (self.time[i] - self.time[i - 1]))
            if self.energy[i] < 0:
                self.energy_recovered[i] = self.energy[i] * self.xx + self.energy_recovered[i - 1]
                self.energy_deployed[i] = self.energy_deployed[i - 1]
                self.total_energy[i] = self.energy[i] * self.xx + self.total_energy[i - 1]
            else:
                self.energy_recovered[i] = self.energy_recovered[i - 1]
                self.energy_deployed[i] = self.energy[i] + self.energy_deployed[i - 1]
                self.total_energy[i] = self.energy[i] + self.total_energy[i - 1]

    def enter_xx(self, a):
        try:
            input_xx = float(self.xx_param_entry.get())
        except ValueError:
            messagebox.showwarning("Warning!", "Value of parameter XX must be a number between 0 and 1.")
            return
        if 1 >= input_xx >= 0:
            self.xx = input_xx
            self.energy_calculations()
            self.max_recovered.set(int(np.abs(np.min(self.energy_recovered))))
            self.max_deployed.set(int(np.max(self.energy_deployed)))
            self.max_net.set(int(np.max(self.total_energy)))
            self.update_plot2()

        else:
            messagebox.showwarning("Warning!", "Value of parameter XX must be a number between 0 and 1.")

    def show_max_values(self):
        self.max_recovered_label = tkinter.Label(self.root, textvariable=self.max_recovered)
        self.max_recovered_label.pack(side=tkinter.LEFT)
        self.max_deployed_label = tkinter.Label(self.root, textvariable=self.max_deployed)
        self.max_deployed_label.pack(side=tkinter.LEFT)
        self.max_net_label = tkinter.Label(self.root, textvariable=self.max_net)
        self.max_net_label.pack(side=tkinter.LEFT)


def import_tdp_data(filename: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads the specified data file and outputs three numpy arrays containing data.
    Data must be separated by tab characters and line breaks.
    First line of data must be 'Time', 'Distance', and 'Power'.
    :param filename: str
        Name of the data file to be imported. File extension included.
    :return: Tuple[np.ndarray, np.ndarray, np.ndarray]
        Three numpy arrays that contain the Time, Distance, and Power data.
    """
    df = pd.read_csv(filename, sep='\t', engine='python')
    time_data = np.array(df['Time'])
    time_data[len(time_data)-1] = 2*time_data[len(time_data)-2] - time_data[len(time_data)-3] # weird outlier fix
    distance_data = np.array(df['Distance'])
    power_data = np.array(df['Power'])
    return time_data, distance_data, power_data


app = GUI()
app.mainloop()

