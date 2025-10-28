import tkinter as tk
import random
import time
import threading
import sys

# 全局变量管理窗口实例
windows = []
MAX_WINDOWS = 37  # 最大窗口数量限制

def set_font():
    """设置支持中文的字体"""
    try:
        return ("SimHei", 12)
    except:
        return ("Arial", 12)

# 祝福语列表
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

# 背景颜色选项
bg_colors = ["#E6F7FF", "#FFE6F2", "#F0F8FF", "#FFF0F5", "#F0FFF0"]

def create_window():
    """创建单个消息窗口"""
    global windows
    
    # 控制窗口数量，超出上限时移除最早创建的窗口
    if len(windows) >= MAX_WINDOWS:
        oldest_window = windows.pop(0)
        if isinstance(oldest_window, tk.Toplevel) and oldest_window.winfo_exists():
            oldest_window.destroy()
    
    # 创建新窗口
    window = tk.Toplevel()
    window.title("亲爱的")
    windows.append(window)
    
    # 随机配置窗口样式
    bg_color = random.choice(bg_colors)
    window.configure(bg=bg_color)
    message = random.choice(messages)
    
    # 添加消息标签
    label = tk.Label(
        window, 
        text=message, 
        font=set_font(),
        bg=bg_color,
        padx=20,
        pady=15
    )
    label.pack()
    
    # 随机定位窗口
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = random.randint(0, screen_width - 200)
    y = random.randint(0, screen_height - 100)
    window.geometry(f"200x100+{x}+{y}")
    
    # 绑定退出快捷键
    window.bind("<Escape>", lambda e: exit_program())
    window.update()

def exit_program():
    """退出程序，清理所有窗口"""
    for window in windows:
        if isinstance(window, tk.Toplevel) and window.winfo_exists():
            window.destroy()
    root.destroy()
    sys.exit(0)

def create_windows_periodically():
    """定时创建窗口，间隔时间逐渐缩短"""
    wait_time = 0.6  # 初始间隔
    min_wait_time = 0.32  # 最小间隔
    decrease_amount = 0.07  # 每次减少的间隔
    
    while True:
        root.after(0, create_window)  # 在主线程中创建窗口
        time.sleep(wait_time)
        
        # 调整下次间隔时间
        wait_time = max(wait_time - decrease_amount, min_wait_time)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 主窗口也绑定退出快捷键
    root.bind("<Escape>", lambda e: exit_program())
    
    # 启动窗口创建线程
    thread = threading.Thread(target=create_windows_periodically, daemon=True)
    thread.start()
    
    root.mainloop()