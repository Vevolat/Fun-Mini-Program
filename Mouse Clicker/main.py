import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import threading
import time
import pyautogui
import keyboard
import json
import os

class MouseClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖱️ 智能鼠标连点器")
        self.root.geometry("420x620")
        self.root.resizable(False, False)
        
        # 设置样式
        self.setup_styles()
        
        # 设置变量
        self.is_clicking = False
        self.click_thread = None
        self.start_key = 'f6'
        self.stop_key = 'f7'
        self.fixed_x = None
        self.fixed_y = None
        self.config_file = "config.json"
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
        
        # 绑定热键
        self.bind_hotkeys()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 配置标签框架样式
        style.configure("Custom.TLabelframe", background="#f0f0f0")
        style.configure("Custom.TLabelframe.Label", font=("微软雅黑", 10, "bold"), foreground="#333333")
        
        # 配置按钮样式
        style.configure("Accent.TButton", font=("微软雅黑", 10, "bold"), padding=6)
        style.map("Accent.TButton",
                  background=[('active', '#4d94ff'), ('pressed', '#1a75ff')],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        
        # 配置普通按钮样式
        style.configure("Normal.TButton", font=("微软雅黑", 9), padding=4)
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🖱️ 鼠标连点器", font=("微软雅黑", 18, "bold"), 
                               foreground="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # 间隔时间设置
        interval_frame = ttk.LabelFrame(main_frame, text="⏱️ 点击间隔(秒)", padding="12", 
                                       style="Custom.TLabelframe")
        interval_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.interval_var = tk.DoubleVar(value=1.0)
        interval_spinbox = ttk.Spinbox(interval_frame, from_=0.001, to=10.0, increment=0.01, 
                                      textvariable=self.interval_var, width=12, font=("Arial", 10))
        interval_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(interval_frame, text="秒", font=("微软雅黑", 9)).grid(row=0, column=1)
        
        # 点击次数设置
        count_frame = ttk.LabelFrame(main_frame, text="🔢 点击次数 (0为无限)", padding="12", 
                                    style="Custom.TLabelframe")
        count_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.count_var = tk.IntVar(value=10)
        count_spinbox = ttk.Spinbox(count_frame, from_=0, to=10000, increment=1, 
                                   textvariable=self.count_var, width=12, font=("Arial", 10))
        count_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        # 鼠标按键选择
        button_frame = ttk.LabelFrame(main_frame, text="🖱️ 鼠标按键", padding="12", 
                                     style="Custom.TLabelframe")
        button_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.button_var = tk.StringVar(value="left")
        left_radio = ttk.Radiobutton(button_frame, text="左键单击", variable=self.button_var, 
                                    value="left", style="TRadiobutton")
        right_radio = ttk.Radiobutton(button_frame, text="右键单击", variable=self.button_var, 
                                     value="right", style="TRadiobutton")
        double_radio = ttk.Radiobutton(button_frame, text="左键双击", variable=self.button_var, 
                                      value="double", style="TRadiobutton")
        
        left_radio.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        right_radio.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)
        double_radio.grid(row=0, column=2, padx=(0, 15), sticky=tk.W)
        
        # 点击位置选择
        position_frame = ttk.LabelFrame(main_frame, text="📍 点击位置", padding="12", 
                                       style="Custom.TLabelframe")
        position_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.position_var = tk.StringVar(value="current")
        current_radio = ttk.Radiobutton(position_frame, text="当前鼠标位置", variable=self.position_var, 
                                       value="current", style="TRadiobutton")
        fixed_radio = ttk.Radiobutton(position_frame, text="固定位置", variable=self.position_var, 
                                     value="fixed", style="TRadiobutton")
        
        current_radio.grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        fixed_radio.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        
        # 固定位置设置按钮
        self.set_position_btn = ttk.Button(position_frame, text="设置位置", 
                                          command=self.set_fixed_position, 
                                          state="normal", style="Normal.TButton")
        self.set_position_btn.grid(row=0, column=2, padx=(10, 0))
        
        # 热键设置
        hotkey_frame = ttk.LabelFrame(main_frame, text="⌨️ 热键设置", padding="12", 
                                     style="Custom.TLabelframe")
        hotkey_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(hotkey_frame, text="开始热键:", font=("微软雅黑", 9)).grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.start_key_btn = ttk.Button(hotkey_frame, text=self.start_key, width=8, 
                                       command=self.change_start_key, style="Normal.TButton")
        self.start_key_btn.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(hotkey_frame, text="停止热键:", font=("微软雅黑", 9)).grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.stop_key_btn = ttk.Button(hotkey_frame, text=self.stop_key, width=8, 
                                      command=self.change_stop_key, style="Normal.TButton")
        self.stop_key_btn.grid(row=0, column=3, padx=(0, 5))
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=(10, 15))
        
        self.start_button = ttk.Button(control_frame, text="▶ 开始", command=self.start_clicking, 
                                      style="Accent.TButton")
        self.stop_button = ttk.Button(control_frame, text="⏹ 停止", command=self.stop_clicking, 
                                     state="disabled", style="Accent.TButton")
        
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="就绪 - 点击'开始'或按 '{}' 键开始连点".format(self.start_key))
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("微软雅黑", 9),
                                foreground="#666666", relief="sunken", padding=5)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 配置列权重
        main_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def start_clicking(self):
        if not self.is_clicking:
            self.is_clicking = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("正在点击...")
            
            # 在新线程中执行点击操作
            self.click_thread = threading.Thread(target=self.perform_clicking)
            self.click_thread.daemon = True
            self.click_thread.start()
    
    def stop_clicking(self):
        self.is_clicking = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("已停止")
    
    def perform_clicking(self):
        interval = self.interval_var.get()
        count = self.count_var.get()
        button = self.button_var.get()
        
        clicks_done = 0
        
        while self.is_clicking and (count == 0 or clicks_done < count):
            try:
                # 根据选择的位置类型确定点击位置
                position_type = self.position_var.get()
                if position_type == "fixed" and self.fixed_x is not None and self.fixed_y is not None:
                    x, y = self.fixed_x, self.fixed_y
                else:
                    x, y = pyautogui.position()
                
                # 执行点击
                if button == "left":
                    pyautogui.click(x, y, button="left")
                elif button == "right":
                    pyautogui.click(x, y, button="right")
                elif button == "double":
                    pyautogui.doubleClick(x, y)
                
                clicks_done += 1
                
                # 更新状态显示
                if count > 0:
                    self.status_var.set(f"点击进度: {clicks_done}/{count}")
                else:
                    self.status_var.set(f"点击次数: {clicks_done}")
                
                # 等待间隔时间，但不小于0.001秒以避免系统限制
                sleep_time = max(0.001, interval)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.status_var.set(f"错误: {str(e)}")
                break
        
        # 完成后自动停止
        if self.is_clicking:
            self.stop_clicking()
            if count > 0:
                self.status_var.set(f"完成 {clicks_done} 次点击")
    
    def bind_hotkeys(self):
        """绑定热键"""
        # 先移除旧的热键绑定
        try:
            keyboard.remove_hotkey(self.start_key)
            keyboard.remove_hotkey(self.stop_key)
        except:
            pass
        
        # 绑定新的热键
        keyboard.add_hotkey(self.start_key, self.start_clicking)
        keyboard.add_hotkey(self.stop_key, self.stop_clicking)
    
    def change_start_key(self):
        """更改开始热键"""
        self.prompt_for_key("开始", "start")
        # 保存配置
        self.save_config()
    
    def change_stop_key(self):
        """更改停止热键"""
        self.prompt_for_key("停止", "stop")
        # 保存配置
        self.save_config()
    
    def prompt_for_key(self, action, key_type):
        """提示用户输入新热键"""
        # 创建顶层窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(f"设置{action}热键")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")
        
        # 提示信息
        label = ttk.Label(dialog, text=f"请按下要设置为{action}功能的键:", font=("微软雅黑", 10))
        label.pack(pady=20)
        
        key_var = tk.StringVar(value="请按键...")
        key_label = ttk.Label(dialog, textvariable=key_var, font=("微软雅黑", 12, "bold"), 
                             foreground="blue")
        key_label.pack(pady=10)
        
        # 检测按键
        def on_key_event(event):
            key = event.name.upper()
            # 过滤特殊键
            if key not in ['SHIFT', 'CTRL', 'ALT', 'WIN', 'ENTER', 'ESC', 'BACKSPACE']:
                key_var.set(key)
                # 更新热键
                if key_type == "start":
                    self.start_key = key
                    self.start_key_btn.config(text=key)
                else:
                    self.stop_key = key
                    self.stop_key_btn.config(text=key)
                
                # 重新绑定热键
                self.bind_hotkeys()
                
                # 更新状态栏提示
                self.status_var.set(f"就绪 - 点击'开始'或按 '{self.start_key}' 键开始连点")
                
                # 关闭对话框
                dialog.after(500, dialog.destroy)
        
        keyboard.on_press(on_key_event)
        
        # 取消按钮
        cancel_btn = ttk.Button(dialog, text="取消", command=dialog.destroy)
        cancel_btn.pack(pady=10)
        
        # 窗口关闭事件
        def on_dialog_close():
            keyboard.unhook(on_key_event)
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

    def set_fixed_position(self):
        """设置固定点击位置"""
        # 获取当前鼠标位置
        x, y = pyautogui.position()
        self.fixed_x, self.fixed_y = x, y
        self.status_var.set(f"✅ 固定位置已设置: ({x}, {y})")
        # 保存配置
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            "interval": self.interval_var.get(),
            "clicks": self.count_var.get(),
            "button": self.button_var.get(),
            "position_type": self.position_var.get(),
            "fixed_x": self.fixed_x,
            "fixed_y": self.fixed_y,
            "start_key": self.start_key,
            "stop_key": self.stop_key
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        """从文件加载配置"""
        if not os.path.exists(self.config_file):
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 应用配置
            self.interval_var.set(config.get("interval", 1.0))
            self.count_var.set(config.get("clicks", 10))
            self.button_var.set(config.get("button", "left"))
            self.position_var.set(config.get("position_type", "current"))
            self.fixed_x = config.get("fixed_x", None)
            self.fixed_y = config.get("fixed_y", None)
            self.start_key = config.get("start_key", "f6")
            self.stop_key = config.get("stop_key", "f7")
            
            # 更新界面显示
            self.start_key_btn.config(text=self.start_key)
            self.stop_key_btn.config(text=self.stop_key)
            
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        # 保存当前配置
        self.save_config()
        self.stop_clicking()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MouseClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
