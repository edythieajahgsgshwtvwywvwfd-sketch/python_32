import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports


class LEDControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STM32 灯光控制台 (BY 404摸不到头脑)")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        # 串口变量
        self.ser = None

        # === 1. 顶部：串口连接区域 ===
        conn_frame = ttk.LabelFrame(root, text="连接设置", padding=10)
        conn_frame.pack(pady=10, padx=10, fill="x")

        # 端口下拉框
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, state="readonly", width=15)
        self.port_combo.pack(side="left", padx=5)
        self.refresh_ports()  # 自动获取当前端口

        # 刷新按钮
        ttk.Button(conn_frame, text="刷新", command=self.refresh_ports, width=5).pack(side="left")

        # 连接按钮
        self.btn_connect = ttk.Button(conn_frame, text="打开串口", command=self.toggle_connection)
        self.btn_connect.pack(side="left", padx=5)

        # === 2. 中部：控制区域 ===
        ctrl_frame = ttk.LabelFrame(root, text="LED 控制", padding=10)
        ctrl_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # 状态指示灯 (用 Canvas 画个圆)
        self.canvas = tk.Canvas(ctrl_frame, width=40, height=40, highlightthickness=0)
        self.canvas.pack(pady=5)
        self.status_light = self.canvas.create_oval(5, 5, 35, 35, fill="gray", outline="gray")  # 初始灰色

        # 按钮容器
        btn_box = ttk.Frame(ctrl_frame)
        btn_box.pack(pady=10)

        # 开灯按钮 (发送 '1')
        self.btn_on = ttk.Button(btn_box, text="💡 点亮 LED", command=lambda: self.send_cmd('1'))
        self.btn_on.pack(side="left", padx=10)

        # 关灯按钮 (发送 '0')
        self.btn_off = ttk.Button(btn_box, text="🌑 熄灭 LED", command=lambda: self.send_cmd('0'))
        self.btn_off.pack(side="left", padx=10)

        # 底部状态栏
        self.status_bar = tk.Label(root, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_ports(self):
        """扫描可用的 COM 端口"""
        ports = list(serial.tools.list_ports.comports())
        port_list = [p.device for p in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)
        else:
            self.port_combo.set("未找到设备")

    def toggle_connection(self):
        """连接/断开串口"""
        if self.ser and self.ser.is_open:
            # 断开连接
            self.ser.close()
            self.btn_connect.config(text="打开串口")
            self.status_bar.config(text="已断开")
            self.port_combo.config(state="readonly")
            self.canvas.itemconfig(self.status_light, fill="gray")
        else:
            # 建立连接
            port = self.port_var.get()
            try:
                # 默认波特率 115200，如果你 CubeMX 设的不一样，请改这里
                self.ser = serial.Serial(port, 115200, timeout=1)
                self.btn_connect.config(text="关闭串口")
                self.status_bar.config(text=f"已连接到 {port}")
                self.port_combo.config(state="disabled")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开串口: {e}")

    def send_cmd(self, cmd):
        """发送指令到 STM32"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(cmd.encode('utf-8'))
                # 更新界面指示灯颜色：1是绿色，0是灰色
                color = "#00FF00" if cmd == '1' else "gray"
                self.canvas.itemconfig(self.status_light, fill=color)
                self.status_bar.config(text=f"发送指令: {cmd}")
            except Exception as e:
                messagebox.showerror("发送失败", str(e))
        else:
            messagebox.showwarning("提示", "请先打开串口连接！")


if __name__ == "__main__":
    root = tk.Tk()
    # 稍微美化一下风格
    style = ttk.Style()
    style.theme_use('clam')
    app = LEDControllerApp(root)
    root.mainloop()
