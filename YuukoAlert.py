import pygame
import tkinter as tk
from PIL import Image,ImageTk
import os
import sys
import atexit
import configparser

CONFIG_FILE = 'config.ini'
PID_FILE = 'yuuko_alert.pid'

def acquire_lock():
	pid = str(os.getpid())
	try:
		with open(PID_FILE, 'x') as pid_file:
			pid_file.write(pid)
	except FileExistsError:
		print("Another instance is already running!")
		sys.exit(1)
	atexit.register(release_lock)

def release_lock():
	if os.path.exists(PID_FILE):
		os.remove(PID_FILE)

def load_config():
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)
	return config['AlertSettings']

def show_alert():
	try:
#		acquire_lock()

		config = load_config()

		pygame.init()
		root = tk.Tk()
		root.resizable(True,True)
		root.geometry(f"{config.getint('window_width')}x{config.getint('window_height')}")
		root.eval('tk::PlaceWindow . center')
		root.iconphoto(False, tk.PhotoImage(file='files/icon.png'))
		root.title(config['window_title'])

		canvas = tk.Canvas(root, width=config.getint('window_width'), height=config.getint('window_height') // 1)
		canvas.pack(padx=5, pady=5)

		img_path = config['image_path']
		if os.path.exists(img_path):
			with Image.open(img_path) as img:
				resized_image= img.resize((80,72), Image.LANCZOS)
				new_image= ImageTk.PhotoImage(resized_image)
				canvas.create_image(8,8, anchor="nw", image=new_image)
		else:
			raise FileNotFoundError(f"Image not found: {img_path}")

		text_label = tk.Label(root, text=config['text_content'], font=('Helvetica LT Std', '12'))
		text_label.place(relx=0.92, rely=0.35, anchor='e')

		close = tk.Button(root, text="        OK        ", font=("Segoe UI", "10"), command=root.destroy)
		close.place(relx=0.5, rely=0.8, anchor='center')

		pygame.mixer.init()
		sound_path = config['sound_path']
		if os.path.exists(sound_path):
			my_sound = pygame.mixer.Sound(sound_path)
			my_sound.play()
			my_sound.set_volume(0.8)
		else:
			print(f"Sound file not found: {sound_path}")


		root.mainloop()

	except Exception as e:
		print(f"Error occurred: {e}")

if __name__ == "__main__":

	try:
		import setproctitle
		setproctitle.setproctitle('Yuuko Alert')
	except ImportError:
		pass

	show_alert()

