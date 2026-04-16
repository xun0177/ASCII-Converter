import tkinter as tk
from tkinter import ttk
import re

class ASCIIDecoderApp:
    def __init__(self, root):
        self.root = root
        root.title("ASCII码转换器")
        root.geometry("600x750")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_frame, text="   转换器   ")
        self.create_converter_tab()

        self.ascii_table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ascii_table_frame, text="   ASCII码表   ")
        self.create_ascii_table_tab()

        self.status = ttk.Label(root, text="就绪", relief="sunken", anchor="w", padding=(5, 2))
        self.status.pack(side="bottom", fill="x")

    def show_status(self, message, is_error=False, is_warning=False):
        self.status.config(text=message)
        if is_error:
            self.status.config(foreground="red")
        elif is_warning:
            self.status.config(foreground="#FF8C00")
        else:
            self.status.config(foreground="black")
        self.root.update_idletasks()

    def create_converter_tab(self):
        mode_frame = ttk.LabelFrame(self.converter_frame, text="转换模式")
        mode_frame.pack(pady=10, padx=10, fill="x")

        self.mode_var = tk.StringVar(value="decode")
        ttk.Radiobutton(mode_frame, text="ASCII码 → 文本（解码）", variable=self.mode_var,
                        value="decode", command=self.on_mode_change).grid(row=0, column=0, padx=20, pady=5)
        ttk.Radiobutton(mode_frame, text="文本 → ASCII码（编码）", variable=self.mode_var,
                        value="encode", command=self.on_mode_change).grid(row=0, column=1, padx=20, pady=5)

        self.encode_options_frame = ttk.Frame(self.converter_frame)
        self.encode_options_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(self.encode_options_frame, text="输出格式：").pack(side="left", padx=5)
        self.format_var = tk.StringVar(value="dec")
        ttk.Radiobutton(self.encode_options_frame, text="十进制", variable=self.format_var, value="dec").pack(side="left", padx=5)
        ttk.Radiobutton(self.encode_options_frame, text="十六进制 (0x)", variable=self.format_var, value="hex").pack(side="left", padx=5)
        ttk.Radiobutton(self.encode_options_frame, text="二进制 (0b)", variable=self.format_var, value="bin").pack(side="left", padx=5)

        ttk.Label(self.encode_options_frame, text="分隔符：").pack(side="left", padx=(20,5))
        self.sep_var = tk.StringVar(value=" ")
        ttk.Entry(self.encode_options_frame, textvariable=self.sep_var, width=5).pack(side="left")
        ttk.Label(self.encode_options_frame, text="（空格、逗号等）").pack(side="left", padx=5)

        self.encode_options_frame.pack_forget()

        input_frame = ttk.LabelFrame(self.converter_frame, text="输入内容")
        input_frame.pack(pady=5, padx=10, fill="x")

        self.input_text = tk.Text(input_frame, height=5, font=('Consolas', 10))
        self.input_text.pack(padx=5, pady=5, fill="x")

        ttk.Button(self.converter_frame, text="转换", command=self.convert).pack(pady=5)

        output_frame = ttk.LabelFrame(self.converter_frame, text="转换结果")
        output_frame.pack(pady=5, padx=10, fill="both", expand=True)

        result_header = ttk.Frame(output_frame)
        result_header.pack(fill="x", padx=5, pady=2)
        ttk.Label(result_header, text="所有内容：").pack(side="left")
        ttk.Button(result_header, text="复制结果", command=self.copy_result).pack(side="right")

        self.result_text = tk.Text(output_frame, height=3, font=('Consolas', 12))
        self.result_text.pack(padx=5, pady=5, fill="x")

        ttk.Label(output_frame, text="详细分解：").pack(anchor="w", padx=5)
        tree_frame = ttk.Frame(output_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.details_tree = ttk.Treeview(tree_frame, columns=("input", "output"), show="headings", height=8)
        self.details_tree.heading("input", text="输入项")
        self.details_tree.heading("output", text="转换结果")
        self.details_tree.column("input", width=300, anchor="center")
        self.details_tree.column("output", width=300, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=scrollbar.set)
        self.details_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def on_mode_change(self):
        if self.mode_var.get() == "encode":
            self.encode_options_frame.pack(pady=5, padx=10, fill="x", after=self.converter_frame.winfo_children()[1])
        else:
            self.encode_options_frame.pack_forget()

    def convert(self):
        mode = self.mode_var.get()
        if mode == "decode":
            self.decode_mixed()
        else:
            self.encode_text()

    def insert_unique_items(self, items):
        seen = set()
        unique_items = []
        for inp, outp in items:
            key = (inp, outp)
            if key not in seen:
                seen.add(key)
                unique_items.append((inp, outp))
        for inp, outp in unique_items:
            self.details_tree.insert("", "end", values=(inp, outp))

    def decode_mixed(self):
        try:
            self.result_text.delete(1.0, tk.END)
            self.details_tree.delete(*self.details_tree.get_children())

            raw = self.input_text.get(1.0, tk.END).strip()
            if not raw:
                self.show_status("请输入要解码的内容", is_warning=True)
                return

            pattern = re.compile(
                r'(?:0x[0-9A-Fa-f]+)'
                r'|(?:0b[01]+)'
                r'|\b[0-9A-Fa-f]+[Hh]\b'
                r'|\b[01]+[Bb]\b'
                r'|\b[0-9]+\b'
            )

            items = []

            def replacer(match):
                token = match.group(0)
                original = token
                try:
                    if token.lower().startswith('0x'):
                        base = 16
                        num_str = token[2:]
                    elif token.lower().startswith('0b'):
                        base = 2
                        num_str = token[2:]
                    elif token[-1].lower() == 'h':
                        base = 16
                        num_str = token[:-1]
                    elif token[-1].lower() == 'b':
                        base = 2
                        num_str = token[:-1]
                    else:
                        base = 10
                        num_str = token

                    decimal = int(num_str, base)
                    if 0 <= decimal <= 255:
                        char = chr(decimal)
                        items.append((original, char))
                        return char
                    else:
                        items.append((original, "数值超出范围(0-255)"))
                        return original
                except Exception as e:
                    items.append((original, f"转换失败: {e}"))
                    return original

            result = pattern.sub(replacer, raw)
            self.result_text.insert(tk.END, result)

            self.insert_unique_items(items)

            self.show_status(f"解码完成 | 识别编码项: {len(items)} | 结果已生成")

        except Exception as e:
            self.show_status(f"解码错误: {e}", is_error=True)

    def encode_text(self):
        try:
            self.result_text.delete(1.0, tk.END)
            self.details_tree.delete(*self.details_tree.get_children())

            text = self.input_text.get(1.0, tk.END).rstrip('\n')
            if not text:
                self.show_status("请输入要编码的文本", is_warning=True)
                return

            fmt = self.format_var.get()
            sep = self.sep_var.get()
            codes = []
            items = []

            for ch in text:
                code_point = ord(ch)
                if code_point > 255:
                    items.append((ch, "非ASCII字符，未转换"))
                    codes.append(ch)
                    continue

                if fmt == "dec":
                    code_str = str(code_point)
                elif fmt == "hex":
                    code_str = f"0x{code_point:02X}"
                else:
                    code_str = f"0b{code_point:08b}"

                items.append((ch, code_str))
                codes.append(code_str)

            result = sep.join(codes)
            self.result_text.insert(tk.END, result)

            self.insert_unique_items(items)

            self.show_status(f"编码完成 | 字符数: {len(text)} | 格式: {fmt}")

        except Exception as e:
            self.show_status(f"编码错误: {e}", is_error=True)

    def copy_result(self):
        result = self.result_text.get(1.0, tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.show_status("结果已复制到剪贴板")
        else:
            self.show_status("没有可复制的内容", is_warning=True)

    def create_ascii_table_tab(self):
        control_frame = ttk.Frame(self.ascii_table_frame)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="ASCII字符表 (0-127)").pack(side="left")
        ttk.Button(control_frame, text="插入选中字符", command=self.insert_selected_char).pack(side="right", padx=5)
        ttk.Button(control_frame, text="插入选中编码(十进制)", command=self.insert_selected_code).pack(side="right", padx=5)

        tree_frame = ttk.Frame(self.ascii_table_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("bin", "oct", "dec", "hex", "char")
        self.ascii_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=22)

        self.ascii_tree.heading("bin", text="二进制")
        self.ascii_tree.heading("oct", text="八进制")
        self.ascii_tree.heading("dec", text="十进制")
        self.ascii_tree.heading("hex", text="十六进制")
        self.ascii_tree.heading("char", text="字符")

        self.ascii_tree.column("bin", width=100, anchor="center")
        self.ascii_tree.column("oct", width=70, anchor="center")
        self.ascii_tree.column("dec", width=70, anchor="center")
        self.ascii_tree.column("hex", width=70, anchor="center")
        self.ascii_tree.column("char", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.ascii_tree.yview)
        self.ascii_tree.configure(yscrollcommand=scrollbar.set)
        self.ascii_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i in range(128):
            bin_str = f"{i:08b}"
            oct_str = f"{i:03o}"
            hex_str = f"{i:02X}"
            char_repr = self.get_ascii_repr(i)
            self.ascii_tree.insert("", "end", values=(bin_str, oct_str, i, hex_str, char_repr))

        self.ascii_tree.bind("<Double-1>", self.on_ascii_double_click)

    def get_ascii_repr(self, code):
        ctrl_names = [
            "NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
            "BS",  "TAB", "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
            "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
            "CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US"
        ]
        if code < 32:
            return ctrl_names[code] if code < len(ctrl_names) else f"Ctrl-{chr(code+64)}"
        elif code == 127:
            return "DEL"
        else:
            return chr(code)

    def on_ascii_double_click(self, event):
        self.insert_selected_char()

    def insert_selected_char(self):
        selected = self.ascii_tree.selection()
        if not selected:
            self.show_status("请先选中一行", is_warning=True)
            return
        item = selected[0]
        values = self.ascii_tree.item(item, "values")
        code = int(values[2])
        char_to_insert = chr(code)
        self.input_text.insert(tk.END, char_to_insert)
        self.notebook.select(0)
        self.show_status(f"已插入字符: {char_to_insert}")

    def insert_selected_code(self):
        selected = self.ascii_tree.selection()
        if not selected:
            self.show_status("请先选中一行", is_warning=True)
            return
        item = selected[0]
        values = self.ascii_tree.item(item, "values")
        code_dec = values[2]
        self.input_text.insert(tk.END, code_dec)
        self.notebook.select(0)
        self.show_status(f"已插入十进制编码: {code_dec}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIDecoderApp(root)
    root.mainloop()