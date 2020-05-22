from PIL import ImageTk, Image
from tkinter import messagebox, filedialog
import tkinter as tk
import pandas as pd
import pandastable as pdt
import csv
import requests
import smtplib
import datetime
import json
import os

"""
purpose of this program:
- allow user interaction
- open and search through a csv file
- pick out a result and plot a relevant graph if desired
- send an email based on the result towards a specified recipient
"""

# Load images
morning_bg = Image.open("images/morningbg.jpg")
aftnoon_bg = Image.open("images/afternoonbg.jpg")
evening_bg = Image.open("images/nightbg.png")
clear_ico = Image.open("images/clear_ico.png")
cloudy_ico = Image.open("images/cloudy_ico.png")
few_cloud_ico = Image.open("images/few_cloud_ico.png")
rain_ico = Image.open("images/rain_ico.png")

bg_dict = {
    "Morning": morning_bg,
    "Afternoon": aftnoon_bg,
    "Evening": evening_bg
}
wt_dict = {
    "Clear": clear_ico,
    "Clouds": [cloudy_ico, few_cloud_ico],
    "Rain": rain_ico
}


# Main application window
class mainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        s_width = 800
        s_height = 600
        s_top_x = self.winfo_screenwidth() // 2 - s_width // 2
        s_top_y = self.winfo_screenheight() // 2 - s_height // 2
        self.geometry(f"{s_width}x{s_height}+{s_top_x}+{s_top_y}")
        self.title("Ahoy Captain")
        self.resizable(0, 0)

        # Frame for holding all the pages of in the app
        container = tk.Frame(self, borderwidth=0, highlightthickness=0)
        container.pack(side="top", fill="both")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Generate all pages simultaneously and store it to a dictionary
        # allows showing the page quickly and not loading the page every single time it is called
        self.frames = {}
        for page in [start_page, email_page, spreadsheet_page]:
            page_name = page.__name__
            frame = page(parent=container, controller=self, WIDTH=s_width, HEIGHT=s_height)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.showframe("start_page")

    def showframe(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


# Starting page
class start_page(tk.Frame):
    def __init__(self, parent, controller, WIDTH, HEIGHT):
        tk.Frame.__init__(self, parent, borderwidth=0, highlightthickness=0)
        self.width = WIDTH
        self.height = HEIGHT
        self.controller = controller
        self.canvas = self.create_background()
        self.create_widgets()

    # Set up canvas and background image
    def create_background(self):
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()
        bg = bg_dict.get(get_time())
        self.bg_img = ImageTk.PhotoImage(bg.resize((self.width, self.height), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_img)
        return self.canvas

    def create_widgets(self):
        # Set up text color according to time of the day
        if get_time() == "Morning":
            c1 = "white"
            c2 = "orange"
            c3 = "grey"
        elif get_time() == "Afternoon":
            c1 = "black"
            c2 = "yellow"
            c3 = "grey"
        else:
            c1 = "white"
            c2 = "magenta"
            c3 = "grey"

        # Get the correct weather icon
        weather = get_weather()
        if weather[0] == "Clear":
            wt_ico = wt_dict.get("Clear")
        elif weather[0] == "Rain":
            wt_ico = wt_dict.get("Rain")
        else:
            if weather[1] == "few clouds":
                wt_ico = wt_dict.get("Clouds")[1]
            else:
                wt_ico = wt_dict.get("Clouds")[0]

        # Main labels
        self.canvas.create_text(20, 20, anchor=tk.NW, fill=f"{c1}", activefill=f"{c2}", font="Times 36",
                                text=f"Good {get_time().lower()}, Captain Chromium!")
        self.canvas.create_text(20, 90, anchor=tk.NW, fill=f"{c1}", font="Times 18",
                                text="What would you like to do on this fine ass day?")
        spreadsheet_btn = tk.Button(self, text="Analyze a file",
                                    command=lambda: self.controller.showframe("spreadsheet_page"))
        self.canvas.create_window(20, 150, anchor=tk.NW, window=spreadsheet_btn)
        send_email_btn = tk.Button(self, text="Send an email", command=lambda: self.controller.showframe("email_page"))
        self.canvas.create_window(20, 190, anchor=tk.NW, window=send_email_btn)

        # Date and weather label
        weather_txt = self.canvas.create_text(self.width - 260, self.height - 60, anchor=tk.NW, fill=f"{c1}",
                                              font="Times 16",
                                              text=f"{datetime.datetime.now().date()}\nWeather: {get_weather()[1]}")
        weather_txt_bbox = self.canvas.bbox(weather_txt)
        weather_txt_bg = self.canvas.create_rectangle(weather_txt_bbox, fill=c3, outline="")
        self.wt_ico = ImageTk.PhotoImage(
            wt_ico.resize((50, weather_txt_bbox[3] - weather_txt_bbox[1]), Image.ANTIALIAS))
        weather_icon = self.canvas.create_image(weather_txt_bbox[2], weather_txt_bbox[1], anchor=tk.NW,
                                                image=self.wt_ico)
        weather_icon_bbox = self.canvas.bbox(weather_icon)
        weather_icon_bg = self.canvas.create_rectangle(weather_icon_bbox, fill=c3, outline="")
        self.canvas.tag_lower(weather_txt_bg, weather_txt)
        self.canvas.tag_lower(weather_icon_bg, weather_icon)


# Page for sending email
class email_page(tk.Frame):
    def __init__(self, parent, controller, WIDTH, HEIGHT):
        tk.Frame.__init__(self, parent, borderwidth=0, highlightthickness=0)
        self.controller = controller
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = self.create_background()
        self.create_widgets()

    def create_background(self):
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()
        bg = bg_dict.get(get_time())
        self.bg_img = ImageTk.PhotoImage(bg.resize((self.width, self.height), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_img)
        return self.canvas

    def create_widgets(self):

        def focus_in(widget, default):
            if widget.get() == default:
                widget.delete(0, "end")
                widget.config(fg="black")

        def focus_out(widget, default):
            if widget.get() == "":
                widget.config(fg="grey")
                widget.insert(0, default)

        def send():
            recipient = recipient_var.get()
            subject = subject_var.get()
            body = body_text.get("1.0", "end-1c")
            confirm = messagebox.askokcancel("Confirmation", "Send email?")
            if confirm == True:
                send_mail(recipient, subject, body)
                recipient_entry.delete(0, "end")
                subject_entry.delete(0, "end")
                body_text.delete("1.0", "end")
            else:
                pass

        back_button = tk.Button(self, text="<", font="Times 8",
                                command=lambda: self.controller.showframe("start_page"))
        self.canvas.create_window(0, 0, anchor=tk.NW, window=back_button)
        title_txt = self.canvas.create_text(20, 40, anchor=tk.NW, font="Times 36", text="SEND EMAIL  ")
        title_txt_bbox = self.canvas.bbox(title_txt)
        title_txt_bg = self.canvas.create_rectangle(title_txt_bbox, outline="", fill="white")
        self.canvas.tag_lower(title_txt_bg, title_txt)

        # Entry boxes for email content
        recipient_var = tk.StringVar()
        subject_var = tk.StringVar()
        recipient_entry = tk.Entry(self, font="Times 14", textvariable=recipient_var, width=30, fg="grey")
        subject_entry = tk.Entry(self, font="Times 14", textvariable=subject_var, width=30, fg="grey")
        body_text = tk.Text(self, font="Times 12", cursor="cross")
        send_button = tk.Button(self, text="Send Email", command=send)

        # Default grey text
        recipient_entry.insert(0, "example123@gmail.com")
        recipient_entry.bind("<FocusIn>", lambda event: focus_in(recipient_entry, "example123@gmail.com"))
        recipient_entry.bind("<FocusOut>", lambda event: focus_out(recipient_entry, "example123@gmail.com"))
        subject_entry.insert(0, "Yohny Yoestar")
        subject_entry.bind("<FocusIn>", lambda event: focus_in(subject_entry, "Yohny Yoestar"))
        subject_entry.bind("<FocusOut>", lambda event: focus_out(subject_entry, "Yohny Yoestar"))

        # Placing the widgets
        self.canvas.create_text(20, 120, anchor=tk.NW, text="Recipient", font="Times 14", fill="white")
        self.canvas.create_window(100, 120, anchor=tk.NW, window=recipient_entry)
        self.canvas.create_text(20, 160, anchor=tk.NW, text="Subject", font="Times 14", fill="white")
        self.canvas.create_window(100, 160, anchor=tk.NW, window=subject_entry)
        self.canvas.create_text(20, 210, anchor=tk.NW, text="Body", font="Times 12", fill="white")
        self.canvas.create_window(20, 240, anchor=tk.NW, window=body_text, height=200, width=600)
        self.canvas.create_window(20, 450, anchor=tk.NW, window=send_button)


# Page for analyzing spreadsheet
class spreadsheet_page(tk.Frame):
    def __init__(self, parent, controller, WIDTH, HEIGHT):
        tk.Frame.__init__(self, parent, borderwidth=0, highlightthickness=0)
        self.controller = controller
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = self.create_background()
        self.create_widgets()

    def create_background(self):
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        bg = bg_dict.get(get_time())
        self.bg_img = ImageTk.PhotoImage(bg.resize((self.width, self.height), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_img)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        return self.canvas


    def create_widgets(self):
        def on_configure(event):
            file_canvas.configure(scrollregion=file_canvas.bbox("all"))

        def open_file():
            file = filedialog.askopenfilename(initialdir="/Documents", title="Select a CSV file",
                                              filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
            file_name = os.path.basename(file)
            file_name_lbl.configure(text=file_name)

            # Change CSV file delimiter to ","
            # by detecting the current delimiter
            # and creating a new file with the correct delimiter
            with open(file, "r") as old_file:
                sniffer = csv.Sniffer().sniff(old_file.read(1024))
                dialect = sniffer.delimiter
                old_file.seek(0)
                csv_reader = csv.reader(old_file, delimiter=dialect)
                with open("temp_file.csv", "w") as new_file:
                    csv_writer = csv.writer(new_file, delimiter=",")
                    for line in csv_reader:
                        csv_writer.writerow(line)

            file = "temp_file.csv"
            df = pd.read_csv(file)
            table = pdt.Table(table_frame, dataframe= df, width=672, height=423, showstatusbar= True, showtoolbar= True)
            table.show()

            # Create scrollbar for the table
            vscrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL)
            vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            vscrollbar.configure(command= file_canvas.yview)
            table_frame.bind("<Configure>", on_configure)
            file_canvas.configure(yscrollcommand= vscrollbar.set)

            table.redraw()

        # Labels and buttons
        back_button = tk.Button(self, text="<", font="Times 8",
                                command=lambda: self.controller.showframe("start_page"))
        open_file_btn = tk.Button(self, text="Open", command=open_file, width=18)
        file_name_lbl = tk.Label(self, text="No CSV file has been selected",
                                 font="Times 20", fg="black", bg="white")

        file_frame = tk.Frame(self, width=750, height=470, bg="white")
        file_canvas = tk.Canvas(file_frame, width= 750, height= 470)
        file_canvas.pack(side= tk.LEFT, fill= tk.BOTH, expand= True)
        table_frame = tk.Frame(file_canvas)
        file_canvas.create_window(0, 0, anchor= tk.NW, window= table_frame)


        self.canvas.create_window(0, 0, anchor=tk.NW, window=back_button)
        self.canvas.create_text(20, 20, anchor=tk.NW, text="Select a file to analyze:", font="Times 15", fill="white")
        self.canvas.create_window(216, 20, anchor=tk.NW, window=open_file_btn)
        self.canvas.create_window(20, 50, anchor=tk.NW, window=file_name_lbl)
        self.canvas.create_window(20, 100, anchor=tk.NW, window=file_frame)


# Get the state of time of the day
def get_time():
    time = datetime.datetime.now().time()
    if 5 <= time.hour < 12:
        return "Morning"
    elif 12 <= time.hour < 17:
        return "Afternoon"
    else:
        return "Evening"


# Get the weather condition of Malang
def get_weather():
    api_request = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q=Malang&appid= YOUR APP ID"
    )
    api = json.loads(api_request.content)
    weather_condition = api["weather"][0]["main"]
    weather_desc = api["weather"][0]["description"]
    return [weather_condition, weather_desc]


# Send email to a specified recipient
def send_mail(recipient, subject, body):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("YOUR EMAIL", "YOUR PASSWORD")
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("YOUR EMAIL",
                    recipient,
                    msg)
    server.quit()


def main():
    app = mainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
