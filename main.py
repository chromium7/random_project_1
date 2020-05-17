from bs4 import BeautifulSoup
from PIL import ImageTk, Image
import tkinter as tk
import matplotlib as plt
import pandas as pd
import csv
import requests
import smtplib
import datetime
import json

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


# This class represent the very first window when the user open the program
class main_window(tk.Frame):
    def __init__(self, WIDTH, HEIGHT, master=None):
        tk.Frame.__init__(self, master, borderwidth=0, highlightthickness=0)
        self.width = WIDTH
        self.height = HEIGHT
        self.pack()
        self.canvas = tk.Canvas(self, width=WIDTH, heigh=HEIGHT)
        self.canvas.pack()
        # Set up background image
        bg = bg_dict.get(get_time())
        self.bg_img = ImageTk.PhotoImage(bg.resize((WIDTH, HEIGHT), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_img)

        self.create_widgets()

    def create_widgets(self):
        # Set up text color according to time of the day
        if get_time() == "Morning":
            c1 = "white"
            c2 = "orange"
            c3 = "grey"
        elif get_time() == "Afternoon":
            c1 = "red"
            c2 = "yellow"
            c3 = "black"
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

        # Date and weather label
        weather_txt = self.canvas.create_text(self.width - 225, self.height - 60, anchor=tk.NW, fill=f"{c1}",
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
        "http://api.openweathermap.org/data/2.5/weather?q=Malang&appid= #YOUR API ID KEY"
    )
    api = json.loads(api_request.content)
    weather_condition = api["weather"][0]["main"]
    weather_desc = api["weather"][0]["description"]
    return [weather_condition, weather_desc]


# Send email to a specified recipient
def send_mail(subject, body):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("a", "b") # a= email, b= password. Hidden for security purposes :)
    msg = f"Subject = {subject}\n\n{body}" 
    server.sendmail("#sender email",
                    "#recipient email",
                    msg)
    server.quit()


def main():
    root = tk.Tk()
    s_width = 800
    s_height = 600
    s_top_x = root.winfo_screenwidth() // 2 - s_width // 2
    s_top_y = root.winfo_screenheight() // 2 - s_height // 2
    root.geometry(f"{s_width}x{s_height}+{s_top_x}+{s_top_y}")
    root.title("Ahoy Captain")
    root.resizable(0, 0)

    front = main_window(s_width, s_height, master=root)
    front.mainloop()


if __name__ == '__main__':
    main()
