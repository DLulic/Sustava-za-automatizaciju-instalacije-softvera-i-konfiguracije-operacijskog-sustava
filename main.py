import tkinter as tk
from Display.MainPage import MainPage

def open_start_page(root, content_frame):
    # Remove current widgets from the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()
    # Add MainPage to the content frame
    page = MainPage(content_frame)
    page.pack(fill="both", expand=True)

def main():
    root = tk.Tk()
    dark_mode = True  # Set to True for dark mode, False for light mode
    if dark_mode:
        root.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
        root.option_add('*TButton*highlightBackground', '#2E2E2E')
        root.option_add('*TButton*highlightColor', '#2E2E2E')
    else:
        root.tk_setPalette(background='#FFFFFF', foreground='#000000')
    root.title("Sustav za automatizaciju instalacije softvera")
    root.geometry("400x200")

    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    # Center the window on the screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 600
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    label = tk.Label(content_frame, text="Sustav za automatizaciju instalacije softvera", wraplength=350)
    label.pack(pady=20)

    btn = tk.Button(content_frame, text="Pokreni", command=lambda: open_start_page(root, content_frame))
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()