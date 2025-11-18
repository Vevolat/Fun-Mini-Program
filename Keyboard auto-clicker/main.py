import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import pyautogui
import keyboard
import json
import os

class KeyboardClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⌨️ 智能键盘连点器")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # 设置变量
        self.is_typing = False
        self.typing_thread = None
        self.is_recording = False
        self.recorded_keys = []
        self.start_key = 'f8'
        self.stop_key = 'f9'
        self.config_file = "keyboard_config.json"
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
        
        # 绑定热键
        self.bind_hotkeys()
        
    def create_widgets(self):
        # 设置样式
        self.root.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.configure("Custom.TLabelframe", background="#f0f0f0", foreground="#2c3e50")
        style.configure("TRadiobutton", background="#f0f0f0", foreground="#34495e")
        style.configure("TLabel", background="#f0f0f0", foreground="#34495e")
        style.configure("Accent.TButton", foreground="white", background="#3498db", 
                       relief="flat", padding=6)
        style.map("Accent.TButton", 
                 background=[('active', '#2980b9')],
                 relief=[('pressed', 'sunken')])
        style.configure("Normal.TButton", foreground="#34495e", background="#ecf0f1", 
                       relief="flat", padding=6)
        style.map("Normal.TButton", 
                 background=[('active', '#d5dbdb')],
                 relief=[('pressed', 'sunken')])
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style="Custom.TLabelframe")
        
        # 标题
        title_label = ttk.Label(main_frame, text="⌨️ 智能键盘连点器", font=("微软雅黑", 20, "bold"), 
                               foreground="#2980b9", background="#f0f0f0")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # 连点模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="🔁 工作模式", padding="12", 
                                   style="Custom.TLabelframe")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.mode_var = tk.StringVar(value="single")
        single_mode_radio = ttk.Radiobutton(mode_frame, text="单个按键连点", variable=self.mode_var, 
                                           value="single", command=self.toggle_mode, 
                                           style="TRadiobutton")
        sequence_mode_radio = ttk.Radiobutton(mode_frame, text="按键序列连点", variable=self.mode_var, 
                                             value="sequence", command=self.toggle_mode, 
                                             style="TRadiobutton")
        record_mode_radio = ttk.Radiobutton(mode_frame, text="录制回放", variable=self.mode_var, 
                                           value="record", command=self.toggle_mode, 
                                           style="TRadiobutton")
        
        single_mode_radio.grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        sequence_mode_radio.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        record_mode_radio.grid(row=0, column=2, padx=(0, 20), sticky=tk.W)
        
        # 单个按键设置
        self.single_key_frame = ttk.LabelFrame(main_frame, text="🔤 单个按键设置", padding="12", 
                                              style="Custom.TLabelframe")
        self.single_key_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        ttk.Label(self.single_key_frame, text="按键:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.single_key_var = tk.StringVar(value="a")
        self.single_key_entry = ttk.Entry(self.single_key_frame, textvariable=self.single_key_var, width=12, 
                                         font=("微软雅黑", 10))
        self.single_key_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(self.single_key_frame, text="说明: 输入要连点的单个按键", font=("微软雅黑", 9), 
                 foreground="#7f8c8d").grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 按键序列设置
        self.sequence_frame = ttk.LabelFrame(main_frame, text="📝 按键序列设置", padding="12", 
                                            style="Custom.TLabelframe")
        self.sequence_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        self.sequence_frame.grid_remove()  # 默认隐藏
        
        ttk.Label(self.sequence_frame, text="按键序列:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.sequence_text = scrolledtext.ScrolledText(self.sequence_frame, width=45, height=5, 
                                                      font=("微软雅黑", 10))
        self.sequence_text.grid(row=1, column=0, columnspan=3, pady=(5, 10))
        self.sequence_text.insert(tk.END, "hello world")
        
        ttk.Label(self.sequence_frame, text="说明: 每行输入一个按键，程序会按顺序连点", font=("微软雅黑", 9), 
                 foreground="#7f8c8d").grid(row=2, column=0, columnspan=3, sticky=tk.W)
        
        # 录制功能
        self.record_frame = ttk.LabelFrame(main_frame, text="⏺️ 录制功能", padding="12", 
                                          style="Custom.TLabelframe")
        self.record_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        self.record_frame.grid_remove()  # 默认隐藏
        
        self.record_button = ttk.Button(self.record_frame, text="开始录制", command=self.toggle_recording, 
                                       style="Normal.TButton")
        self.record_button.grid(row=0, column=0, padx=(0, 15))
        
        self.play_record_button = ttk.Button(self.record_frame, text="播放录制", command=self.play_recording, 
                                            state="disabled", style="Normal.TButton")
        self.play_record_button.grid(row=0, column=1, padx=(0, 15))
        
        self.clear_record_button = ttk.Button(self.record_frame, text="清空录制", command=self.clear_recording, 
                                             style="Normal.TButton")
        self.clear_record_button.grid(row=0, column=2, padx=(0, 15))
        
        self.record_status_var = tk.StringVar(value="未录制")
        record_status_label = ttk.Label(self.record_frame, textvariable=self.record_status_var, 
                                       font=("微软雅黑", 9), foreground="#e74c3c")
        record_status_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        # 间隔时间设置
        interval_frame = ttk.LabelFrame(main_frame, text="⏱️ 间隔时间(秒)", padding="12", 
                                       style="Custom.TLabelframe")
        interval_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.interval_var = tk.DoubleVar(value=0.1)
        interval_spinbox = ttk.Spinbox(interval_frame, from_=0.001, to=10.0, increment=0.01, 
                                      textvariable=self.interval_var, width=12, font=("微软雅黑", 10))
        interval_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(interval_frame, text="秒", font=("微软雅黑", 10)).grid(row=0, column=1)
        
        # 点击次数设置
        count_frame = ttk.LabelFrame(main_frame, text="🔢 点击次数 (0为无限)", padding="12", 
                                    style="Custom.TLabelframe")
        count_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        self.count_var = tk.IntVar(value=10)
        count_spinbox = ttk.Spinbox(count_frame, from_=0, to=10000, increment=1, 
                                   textvariable=self.count_var, width=12, font=("微软雅黑", 10))
        count_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        # 热键设置
        hotkey_frame = ttk.LabelFrame(main_frame, text="⌨️ 热键设置", padding="12", 
                                     style="Custom.TLabelframe")
        hotkey_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(hotkey_frame, text="开始热键:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.start_key_btn = ttk.Button(hotkey_frame, text=self.start_key.upper(), width=10, 
                                       command=self.change_start_key, style="Normal.TButton")
        self.start_key_btn.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(hotkey_frame, text="停止热键:", font=("微软雅黑", 10)).grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        self.stop_key_btn = ttk.Button(hotkey_frame, text=self.stop_key.upper(), width=10, 
                                      command=self.change_stop_key, style="Normal.TButton")
        self.stop_key_btn.grid(row=0, column=3, padx=(0, 10))
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=8, column=0, columnspan=3, pady=(15, 15))
        
        self.start_button = ttk.Button(control_frame, text="▶ 开始连点", command=self.start_typing, 
                                      style="Accent.TButton")
        self.stop_button = ttk.Button(control_frame, text="⏹ 停止连点", command=self.stop_typing, 
                                     state="disabled", style="Accent.TButton")
        
        self.start_button.grid(row=0, column=0, padx=(0, 15))
        self.stop_button.grid(row=0, column=1, padx=(0, 15))
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="就绪 - 点击'开始连点'或按 '{}' 键开始连点".format(self.start_key.upper()))
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("微软雅黑", 9),
                                foreground="#7f8c8d", relief="sunken", padding=8)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 配置列权重
        main_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def toggle_mode(self):
        """切换工作模式"""
        mode = self.mode_var.get()
        
        # 隐藏所有模式框架
        self.single_key_frame.grid_remove()
        self.sequence_frame.grid_remove()
        self.record_frame.grid_remove()
        
        # 显示当前模式框架
        if mode == "single":
            self.single_key_frame.grid()
        elif mode == "sequence":
            self.sequence_frame.grid()
        elif mode == "record":
            self.record_frame.grid()
            
    def toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording:
            # 开始录制
            self.is_recording = True
            self.record_button.config(text="停止录制")
            self.record_status_var.set("正在录制...")
            self.recorded_keys = []
            
            # 开始监听按键
            keyboard.start_recording()
        else:
            # 停止录制
            self.is_recording = False
            self.record_button.config(text="开始录制")
            
            # 停止监听并获取录制的按键
            recorded = keyboard.stop_recording()
            if recorded:
                # 处理录制的按键
                for event in recorded:
                    if event.event_type == keyboard.KEY_DOWN:
                        self.recorded_keys.append(event.name)
                
                self.record_status_var.set(f"录制完成，共 {len(self.recorded_keys)} 个按键")
                self.play_record_button.config(state="normal")
            else:
                self.record_status_var.set("录制完成，无按键记录")
                self.play_record_button.config(state="disabled")
                
    def play_recording(self):
        """播放录制的按键"""
        if self.recorded_keys:
            self.status_var.set(f"正在播放录制内容 ({len(self.recorded_keys)} 个按键)")
            
            # 在新线程中播放录制的按键
            play_thread = threading.Thread(target=self._play_recorded_keys)
            play_thread.daemon = True
            play_thread.start()
            
    def _play_recorded_keys(self):
        """在后台线程中播放录制的按键"""
        try:
            interval = self.interval_var.get()
            clicks = self.count_var.get()
            
            count = 0
            while self.is_typing and (clicks == 0 or count < clicks):
                for key in self.recorded_keys:
                    if not self.is_typing:
                        break
                    pyautogui.press(key)
                    time.sleep(interval)
                count += 1
        except Exception as e:
            print(f"播放录制内容出错: {e}")
            self.status_var.set(f"播放录制内容出错: {str(e)}")
        finally:
            self.stop_typing()
            if self.is_typing:  # 正常完成
                self.status_var.set(f"录制播放完成，共执行 {count} 轮")
            
    def clear_recording(self):
        """清空录制内容"""
        self.recorded_keys = []
        self.record_status_var.set("未录制")
        self.play_record_button.config(state="disabled")
        
    def start_typing(self):
        """开始连点"""
        if not self.is_typing:
            self.is_typing = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("正在连点...")
            
            # 在新线程中执行连点操作
            self.typing_thread = threading.Thread(target=self.perform_typing)
            self.typing_thread.daemon = True
            self.typing_thread.start()
            
    def stop_typing(self):
        """停止连点"""
        self.is_typing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("已停止")
        
    def perform_typing(self):
        """执行连点操作"""
        mode = self.mode_var.get()
        interval = self.interval_var.get()
        count = self.count_var.get()
        
        try:
            if mode == "single":
                self._perform_single_key_typing(interval, count)
            elif mode == "sequence":
                self._perform_sequence_typing(interval, count)
            elif mode == "record":
                self._play_recorded_keys()
                
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            
        # 完成后自动停止
        if self.is_typing:
            self.stop_typing()
            
    def _perform_single_key_typing(self, interval, count):
        """执行单个按键连点"""
        try:
            key = self.single_key_var.get().strip()
            if not key:
                self.status_var.set("错误: 请输入要连点的按键")
                return
                
            presses_done = 0
            
            while self.is_typing and (count == 0 or presses_done < count):
                pyautogui.press(key)
                presses_done += 1
                
                # 更新状态显示
                if count > 0:
                    self.status_var.set(f"按键进度: {presses_done}/{count}")
                else:
                    self.status_var.set(f"按键次数: {presses_done}")
                    
                # 等待间隔时间
                time.sleep(max(0.001, interval))
                
        except Exception as e:
            print(f"连点执行出错: {e}")
            self.status_var.set(f"连点出错: {str(e)}")
        finally:
            if self.is_typing:
                self.status_var.set(f"完成 {presses_done} 次按键")
            
    def _perform_sequence_typing(self, interval, count):
        """执行按键序列连点"""
        try:
            # 获取文本内容并分割成按键列表
            text_content = self.sequence_text.get("1.0", tk.END).strip()
            if not text_content:
                self.status_var.set("错误: 请输入按键序列")
                return
                
            keys = [line.strip() for line in text_content.split('\n') if line.strip()]
            if not keys:
                self.status_var.set("错误: 请输入有效的按键序列")
                return
                
            sequences_done = 0
            
            while self.is_typing and (count == 0 or sequences_done < count):
                for key in keys:
                    if not self.is_typing:
                        break
                        
                    pyautogui.press(key)
                    time.sleep(max(0.001, interval))
                    
                sequences_done += 1
                
                # 更新状态显示
                if count > 0:
                    self.status_var.set(f"序列进度: {sequences_done}/{count}")
                else:
                    self.status_var.set(f"序列次数: {sequences_done}")
                    
        except Exception as e:
            print(f"序列连点执行出错: {e}")
            self.status_var.set(f"序列连点出错: {str(e)}")
        finally:
            if self.is_typing:
                self.status_var.set(f"完成 {sequences_done} 次序列")
            
    def bind_hotkeys(self):
        """绑定热键"""
        try:
            # 先移除旧的热键绑定
            try:
                keyboard.remove_hotkey(self.start_key)
                keyboard.remove_hotkey(self.stop_key)
            except:
                pass
            
            # 绑定新的热键
            keyboard.add_hotkey(self.start_key, self.start_typing)
            keyboard.add_hotkey(self.stop_key, self.stop_typing)
        except Exception as e:
            print(f"绑定热键失败: {e}")
            messagebox.showerror("错误", f"绑定热键失败: {e}")
        
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
            key = event.name
            # 过滤特殊键
            if key.lower() not in ['shift', 'ctrl', 'alt', 'win', 'enter', 'esc', 'backspace']:
                # 更新热键
                if key_type == "start":
                    self.start_key = key.lower()
                    self.start_key_btn.config(text=key.upper())
                else:
                    self.stop_key = key.lower()
                    self.stop_key_btn.config(text=key.upper())
                
                # 重新绑定热键
                self.bind_hotkeys()
                
                # 更新状态栏提示
                if key_type == "start":
                    self.status_var.set(f"就绪 - 点击'开始'或按 '{key.upper()}' 键开始连点")
                else:
                    self.status_var.set(f"就绪 - 点击'开始'或按 '{self.start_key.upper()}' 键开始连点")
                
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

    def save_config(self):
        """保存配置到文件"""
        try:
            config = {
                "mode": self.mode_var.get(),
                "single_key": self.single_key_var.get(),
                "sequence": self.sequence_text.get("1.0", tk.END).strip(),
                "interval": self.interval_var.get(),
                "clicks": self.count_var.get(),
                "start_key": self.start_key,
                "stop_key": self.stop_key,
                "recorded_keys": self.recorded_keys
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
            messagebox.showerror("错误", f"保存配置失败: {e}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if not os.path.exists(self.config_file):
                return
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 应用配置
            self.mode_var.set(config.get("mode", "single"))
            self.single_key_var.set(config.get("single_key", "a"))
            self.interval_var.set(config.get("interval", 0.1))
            self.count_var.set(config.get("clicks", 10))
            self.start_key = config.get("start_key", "f8")
            self.stop_key = config.get("stop_key", "f9")
            self.recorded_keys = config.get("recorded_keys", [])
            
            # 更新序列文本
            sequence = config.get("sequence", "")
            if sequence:
                self.sequence_text.delete("1.0", tk.END)
                self.sequence_text.insert("1.0", sequence)
            
            # 更新界面显示
            self.start_key_btn.config(text=self.start_key.upper())
            self.stop_key_btn.config(text=self.stop_key.upper())
            
            # 更新录制状态
            if self.recorded_keys:
                self.record_status_var.set(f"已加载录制内容，共 {len(self.recorded_keys)} 个按键")
                self.play_record_button.config(state="normal")
                
            # 切换到正确的模式
            self.toggle_mode()
            
        except FileNotFoundError:
            # 配置文件不存在是正常情况，不需要报错
            pass
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            messagebox.showerror("错误", "配置文件格式错误，请检查或删除配置文件")
        except Exception as e:
            print(f"加载配置失败: {e}")
            messagebox.showerror("错误", f"加载配置失败: {e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        # 保存当前配置
        self.save_config()
        self.stop_typing()
        self.root.destroy()

def main   主要():
    root = tk.Tk()
    app = KeyboardClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
