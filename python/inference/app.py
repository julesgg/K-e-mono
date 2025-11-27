import tkinter as tk
from tkinter import messagebox, Toplevel, Canvas
from tkinter import PhotoImage
import subprocess
import threading
import random
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


# ========== GLOBAL STATE ==========
data_reception_process = None
STOP_SIGNAL_PATH = "stop_signal.txt"


# ========== HELPERS ==========

def run_in_thread(target):
    """Utility to run long actions in background."""
    thread = threading.Thread(target=target)
    thread.start()


# ========== START / STOP DATA COLLECTION ==========

def start_data_reception():
    global data_reception_process

    # Remove previous stop signal if exists
    if os.path.exists(STOP_SIGNAL_PATH):
        os.remove(STOP_SIGNAL_PATH)

    try:
        data_reception_process = subprocess.Popen(
            ["python", "python/acquisition/data_reception.py"]
        )
        messagebox.showinfo("Recording", "Data recording started.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not start recording:\n{e}")


def stop_data_reception():
    global data_reception_process

    if data_reception_process:
        try:
            # Write stop signal
            with open(STOP_SIGNAL_PATH, "w") as f:
                f.write("stop")

            data_reception_process.wait(timeout=5)
            data_reception_process = None
            messagebox.showinfo("Recording", "Recording stopped.")

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping recording:\n{e}")
    else:
        messagebox.showwarning("Warning", "No active recording.")


# ========== DISPLAY GRAPH WINDOW ==========

def show_results_graphs():
    graph_window = Toplevel(root)
    graph_window.title("Sensor plots")
    graph_window.geometry("900x700")

    fig, axes = plt.subplots(5, 1, figsize=(8, 10), sharex=True)
    plt.subplots_adjust(hspace=0.5)

    sensor_files = {
        1: "data/processed/data_capteur1_filtered.csv",
        2: "data/processed/data_capteur2_filtered.csv",
        3: "data/processed/data_capteur3_filtered.csv",
        4: "data/processed/data_capteur4_filtered.csv",
        5: "data/processed/data_capteur5_filtered.csv"
    }

    titles = ["Right arm", "Right lapel", "Neck", "Left lapel", "Left arm"]
    colors = ["blue", "red", "green", "purple", "orange"]

    for i, ax in enumerate(axes):
        file = sensor_files[i + 1]
        if os.path.exists(file):
            df = pd.read_csv(file)
            if not df.empty:
                ax.plot(df["Timestamp"], df["Resistance"], color=colors[i], lw=2)
        ax.set_title(titles[i], fontsize=12)
        ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack()


# ========== DISPLAY JUDOKA IMAGE WITH STATS ==========

def show_results_with_image(percentages, total_saisies):
    result_window = Toplevel(root)
    result_window.title("Training results")
    result_window.geometry("800x600")

    try:
        image = Image.open("documentation/judoka.jpg")
    except:
        messagebox.showerror("Error", "Missing image: documentation/judoka.jpg")
        return

    image = image.resize((600, 600))
    draw = ImageDraw.Draw(image)

    # Positions of sensors on the judogi image
    sensor_positions = {
        1: (200, 200),
        2: (270, 150),
        3: (320, 100),
        4: (310, 150),
        5: (400, 200)
    }

    sensor_colors = {
        1: (0, 0, 255),
        2: (255, 0, 0),
        3: (0, 128, 0),
        4: (128, 0, 128),
        5: (255, 165, 0)
    }

    for id, (x, y) in sensor_positions.items():
        percentage = percentages.get(id, 0)
        count = int(percentage * total_saisies / 100)

        opacity = int(percentage * 2.55)
        color = (*sensor_colors[id], opacity)

        draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill=color)
        draw.text((x + 15, y), f"{count} ({percentage:.1f}%)", fill="white")

    tk_image = ImageTk.PhotoImage(image)
    canvas = Canvas(result_window, width=600, height=600)
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.image = tk_image
    canvas.pack()

    close_button = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_button.pack(pady=10)


# ========== PROCESSING PIPELINE ==========

def process_results():
    """
    Runs traitement_all_sensors.py to compute the number of grips per sensor
    and displays numerical + graphical results.
    """
    try:
        result = subprocess.run(
            ["python", "python/inference/traitement_all_sensors.py"],
            capture_output=True,
            text=True
        )

        output_lines = result.stdout.split("\n")
        results = [line for line in output_lines if "Capteur" in line]

        if not results:
            messagebox.showwarning("No data", "No sensor data detected.")
            return

        total_saisies = sum(int(line.split(":")[1].split()[0]) for line in results)
        if total_saisies == 0:
            messagebox.showwarning("No grips", "No grips detected.")
            return

        percentages = {
            i + 1: int(line.split(":")[1].split()[0]) / total_saisies * 100
            for i, line in enumerate(results)
        }

        show_results_with_image(percentages, total_saisies)
        show_results_graphs()

    except Exception as e:
        messagebox.showerror("Error", f"Processing failed:\n{e}")


# ========== GUI ==========

root = tk.Tk()
root.title("K'e-mono app")
root.geometry("500x400")
root.resizable(False, False)
root.configure(bg="#f4f4f4")

title_label = tk.Label(root, text="K'e-mono", font=("Helvetica", 20, "bold"),
                       fg="#333333", bg="#f4f4f4")
title_label.pack(pady=10)

button_style = {
    "font": ("Helvetica", 14),
    "bg": "#007BFF",
    "fg": "white",
    "activebackground": "#0056b3",
    "activeforeground": "white",
    "bd": 3,
    "width": 25
}

tk.Button(root, text="Start training",
          command=lambda: run_in_thread(start_data_reception),
          **button_style).pack(pady=10)

tk.Button(root, text="End training",
          command=stop_data_reception,
          **button_style).pack(pady=10)

tk.Button(root, text="View results",
          command=lambda: run_in_thread(process_results),
          **button_style).pack(pady=10)

tk.Button(root, text="Exit",
          command=root.quit,
          **button_style).pack(pady=40)

footer_label = tk.Label(root, text="© 2025 Smart kimono project",
                        font=("Helvetica", 10), fg="#888888", bg="#f4f4f4")
footer_label.pack(side="bottom", pady=5)

root.mainloop()
