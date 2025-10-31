import tkinter as tk
import random
import time
import threading
import sys
import math

windows = []
MAX_WINDOWS = 64  # 控制爱心密度

def generate_heart_points(num_points, scale=1.0, offset_x=0, offset_y=0):
    points = []
    for i in range(num_points):
        t = i / num_points * 2 * math.pi
        x = 16 * math.pow(math.sin(t), 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        x = x * scale + offset_x
        y = -y * scale + offset_y  # 修正屏幕Y轴方向
        points.append((int(x), int(y)))
    return points

def get_font():
    return ("SimHei", 12)

# 表白风格消息列表
messages = [
    "遇见你之后，连冬天的风都变温柔了",
    "想和你一起踩雪，更想和你一直到老",
    "我的心很小，刚好只装得下一个你",
    "每次看到你，都觉得世界特别可爱",
    "你一笑，我连冬天的寒冷都忘了",
    "往后的每一个冬天，都想有你在身边",
    "喜欢你这件事，我想藏都藏不住",
    "和你在一起的时光，都是甜甜的",
    "你是我冬天里最想拥抱的温暖",
    "只要有你，平凡的日子也会发光",
    "我的偏爱和例外，永远只给你一个人",
    "见到你的那一刻，我就知道心动了",
    "想把所有的温柔，都攒起来给你",
    "你在，冬天才不算辜负好时光"
]

bg_colors = ["#FFE6F2", "#FFCCE5", "#FFB6C1", "#FFA07A", "#FF8C9E"]  # 偏粉色系，贴合表白氛围

heart_points = []

def make_window(index):
    global windows, heart_points
    
    if len(windows) >= MAX_WINDOWS:
        old_window = windows.pop(0)
        if hasattr(old_window, 'winfo_exists') and old_window.winfo_exists():
            old_window.destroy()
    
    window = tk.Toplevel()
    window.title("喜欢你呀")  # 表白主题标题
    windows.append(window)
    
    bg_color = random.choice(bg_colors)
    window.configure(bg=bg_color)
    message = random.choice(messages)
    
    label = tk.Label(window, text=message, font=get_font(), bg=bg_color, padx=20, pady=15)
    label.pack()
    
    x, y = heart_points[index % len(heart_points)]
    window.geometry(f"250x120+{x}+{y}")
    window.bind("<Escape>", lambda e: quit_program())
    window.update()

def quit_program():
    for window in windows:
        if hasattr(window, 'winfo_exists') and window.winfo_exists():
            window.destroy()
    root.destroy()
    sys.exit(0)

def keep_creating_windows():
    wait_time, min_wait, decrease = 0.44, 0.2, 0.04
    index = 0
    while True:
        root.after(0, make_window, index)
        index += 1
        time.sleep(wait_time)
        wait_time = max(wait_time - decrease, min_wait)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    root.bind("<Escape>", lambda e: quit_program())
    
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    heart_points = generate_heart_points(MAX_WINDOWS, scale=25, offset_x=center_x, offset_y=center_y)
    
    thread = threading.Thread(target=keep_creating_windows, daemon=True)
    thread.start()
    root.mainloop()