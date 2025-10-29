import tkinter as tk
import random
import time
import threading
import sys

# 存储所有创建的窗口
windows = []
MAX_WINDOWS = 52  # 最多同时显示52个窗口

def get_font():
    """设置支持中文的字体"""
    # 尝试几种常见的中文字体
    return ("SimHei", 12)  # 黑体通常都能支持

# 这里是一些温馨的话语
messages = [
    "梦想成真", "别熬夜", "今天有过的开心嘛", "祝你开心",
    "期待我们下次见面", "在干嘛", "很高兴见到你",
    "愿所有的梦想都成真", "记得多喝水呀", "今天也要加油哦",
    "你笑起来真好看", "累了就休息一下吧", "天气变凉了，注意保暖",
    "别给自己太大压力", "见到你真的很开心", "希望你每天都有小确幸",
    "你的努力我都看在眼里", "有空一起去喝杯奶茶吧", "今天的你也很棒呀",
    "好好吃饭，照顾好自己", "想和你分享今天的趣事", "你值得所有美好的事物",
    "不管怎样，我都支持你", "愿你每天都能睡个好觉", "看到你开心，我也会开心",
    "慢慢来，一切都会好的", "记得给自己一点放松的时间", "今天的风好像在说想你",
    "你的存在本身就很有意义", "希望你每天都笑得像个孩子", "再忙也要记得休息呀",
    "你比你想象中更优秀", "愿你的每一天都充满阳光", "有你在的日子很安心",
    "别担心，一切都会顺利的"
]

# 窗口背景颜色，选个柔和点的
bg_colors = ["#E6F7FF", "#FFE6F2", "#F0F8FF", "#FFF0F5", "#F0FFF0"]

def make_window():
    """创建一个小窗口显示温馨话语"""
    global windows
    
    # 如果窗口太多了，就把最早的关掉
    if len(windows) >= MAX_WINDOWS:
        old_window = windows.pop(0)  # 取出第一个窗口
        # 检查窗口是否还存在
        if hasattr(old_window, 'winfo_exists') and old_window.winfo_exists():
            old_window.destroy()  # 关掉它
    
    # 创建新窗口
    window = tk.Toplevel()
    window.title("给你的小心心")
    windows.append(window)  # 记住这个窗口
    
    # 随机选个背景色和话语
    bg_color = random.choice(bg_colors)
    window.configure(bg=bg_color)
    message = random.choice(messages)
    
    # 显示话语
    label = tk.Label(
        window, 
        text=message, 
        font=get_font(),
        bg=bg_color,
        padx=20,
        pady=15
    )
    label.pack()
    
    # 把窗口放在屏幕的随机位置
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = random.randint(0, screen_width - 200)
    y = random.randint(0, screen_height - 100)
    window.geometry(f"200x100+{x}+{y}")
    
    # 按ESC键可以退出程序
    window.bind("<Escape>", lambda e: quit_program())
    window.update()

def quit_program():
    """退出程序"""
    # 关掉所有窗口
    for window in windows:
        if hasattr(window, 'winfo_exists') and window.winfo_exists():
            window.destroy()
    
    # 关闭主窗口并退出
    root.destroy()
    sys.exit(0)

def keep_creating_windows():
    """不停地创建新窗口"""
    wait_time = 0.44  # 开始间隔0.44秒
    min_wait_time = 0.2  # 最短间隔0.2秒
    decrease_amount = 0.04  # 每次减少0.04秒
    
    while True:
        # 在主线程中创建窗口
        root.after(0, make_window)
        time.sleep(wait_time)
        
        # 逐渐加快创建速度，但不会快于最短间隔
        wait_time = max(wait_time - decrease_amount, min_wait_time)

# 程序入口
if __name__ == "__main__":
    # 创建主窗口（但不显示它）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 主窗口也绑定ESC键退出
    root.bind("<Escape>", lambda e: quit_program())
    
    # 启动一个线程来不停地创建窗口
    thread = threading.Thread(target=keep_creating_windows, daemon=True)
    thread.start()
    
    # 开始事件循环
    root.mainloop()
