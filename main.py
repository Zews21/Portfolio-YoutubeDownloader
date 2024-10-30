import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading


# Progress callback function
def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('_percent_str', '0%')
        progress_var.set(float(downloaded.strip('%')))
        root.update_idletasks()


# Function to fetch available resolutions for a given video
def fetch_video_info(link):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get('title', 'Unknown Title')
            resolutions = sorted(set([f['height'] for f in info['formats'] if f['vcodec'] != 'none' and f['height']]))
            return title, resolutions
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve video info: {str(e)}")
        return None, []


# Function to populate video title and available resolutions
def get_video_info():
    link = url_entry.get()
    if not link:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    title, available_resolutions = fetch_video_info(link)
    if title:
        title_var.set(f"Title: {title}")
    else:
        title_var.set("Title: Unknown")

    # Update the resolution dropdown
    if available_resolutions:
        resolution_menu["menu"].delete(0, "end")
        for res in available_resolutions:
            resolution_menu["menu"].add_command(label=str(res), command=tk._setit(resolution_var, res))
        resolution_var.set(available_resolutions[-1])
    else:
        messagebox.showerror("Error", "No resolutions available for this video.")


# Function to download video
def download_video():
    link = url_entry.get()
    if not link:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    ydl_opts = {
        'format': f'bestvideo[height<={resolution_var.get()}]+bestaudio/best[height<={resolution_var.get()}]',
        'progress_hooks': [progress_hook],
        'outtmpl': f"{download_path.get()}/%(title)s.%(ext)s",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        messagebox.showinfo("Success", "Download completed!")
    except yt_dlp.utils.DownloadError as e:
        if "ffmpeg" in str(e):
            messagebox.showerror("Error", "FFmpeg is required for merging formats. Please install FFmpeg.")
        else:
            messagebox.showerror("Error", f"Failed to download video: {str(e)}")
    finally:
        progress_var.set(0)


# Function to download audio
def download_audio():
    link = url_entry.get()
    if not link:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'progress_hooks': [progress_hook],
        'outtmpl': f"{download_path.get()}/%(title)s.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        messagebox.showinfo("Success", "Audio download completed!")
    except yt_dlp.utils.DownloadError as e:
        if "ffmpeg" in str(e):
            messagebox.showerror("Error", "FFmpeg is required for merging formats. Please install FFmpeg.")
        else:
            messagebox.showerror("Error", f"Failed to download audio: {str(e)}")
    finally:
        progress_var.set(0)


# Main window setup
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("500x450")

# Large title label
app_title = tk.Label(root, text="YouTube Downloader", font=("Helvetica", 18, "bold"))
app_title.grid(row=0, column=0, columnspan=3, pady=10)

# URL entry
tk.Label(root, text="YouTube URL:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

# Get Video Info Button
get_info_button = tk.Button(root, text="Get Video Info", command=get_video_info)
get_info_button.grid(row=2, column=1, pady=5)

# Video title display
title_var = tk.StringVar()
title_label = tk.Label(root, textvariable=title_var, wraplength=400, font=("Helvetica", 10, "italic"))
title_label.grid(row=3, column=0, columnspan=3, pady=5)

# Resolution dropdown
tk.Label(root, text="Select Resolution:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
resolution_var = tk.StringVar(root)
resolution_var.set("720")  # default resolution
resolution_menu = tk.OptionMenu(root, resolution_var, "720")  # starts with a default option
resolution_menu.grid(row=4, column=1, sticky="w", padx=5, pady=5)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=5, column=0, columnspan=3, pady=10, padx=20, sticky="we")

# Folder selection
tk.Label(root, text="Save to:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
download_path = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=download_path, width=30)
folder_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
tk.Button(root, text="Browse", command=lambda: download_path.set(filedialog.askdirectory())).grid(row=6, column=2, padx=5, pady=5, sticky="w")

# Buttons for actions
tk.Button(root, text="Download Video", command=lambda: threading.Thread(target=download_video).start()).grid(row=7, column=1, pady=10)
tk.Button(root, text="Download Audio", command=lambda: threading.Thread(target=download_audio).start()).grid(row=8, column=1, pady=10)

# Adjust column weights for resizing
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# Run the main Tkinter event loop
root.mainloop()
