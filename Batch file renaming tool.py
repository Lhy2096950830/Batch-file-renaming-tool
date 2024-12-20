import os
import re
from tkinter import Tk, Label, Entry, Button, filedialog, Checkbutton, IntVar, StringVar, messagebox, Toplevel, Listbox
from datetime import datetime

# 日志记录函数
def log_rename(folder_path, old_name, new_name):
    if log_var.get():  # 如果选择记录日志
        log_file = os.path.join(folder_path, "rename_log.txt")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - {old_name} -> {new_name}\n")

# 提取学号和姓名的辅助函数
def extract_student_info(filename):
    match = re.search(r"(\d{10}[A-Za-z]?).*?([\u4e00-\u9fa5]+)", filename)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

# 文件重命名主逻辑
def rename_files():
    folder_path = folder_path_entry.get()
    include_subdirs = subdir_var.get()

    if not folder_path:
        messagebox.showerror("错误", "请选择文件夹！")
        return

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        messagebox.showerror("错误", "输入的文件夹路径无效！")
        return

    renamed_count = 0

    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            old_path = os.path.join(root, filename)
            name, ext = os.path.splitext(filename)

            # 提取学号和姓名
            student_id, student_name = extract_student_info(name)
            if student_id and student_name:
                new_name = student_id + student_name + ext
            else:
                new_name = name + ext

            # 执行替换规则
            for old, new in replacement_rules:
                new_name = new_name.replace(old, new)

            # 插入文本
            if insert_text_var.get():
                insert_position = int(insert_position_var.get() or 0)
                insert_text = insert_text_entry.get()
                if 0 <= insert_position < len(new_name):
                    new_name = new_name[:insert_position] + insert_text + new_name[insert_position:]

            # 移除指定字符
            if remove_text_var.get():
                chars_to_remove = remove_text_entry.get()
                for char in chars_to_remove:
                    new_name = new_name.replace(char, "")

            # 保留指定字符（移除其他字符）
            if retain_text_var.get():
                chars_to_retain = retain_text_entry.get()
                new_name = "".join([c for c in new_name if c in chars_to_retain]) + ext

            new_path = os.path.join(root, new_name)

            if os.path.exists(new_path):
                messagebox.showwarning("警告", f"目标文件已存在，跳过：{new_name}")
                continue

            try:
                os.rename(old_path, new_path)
                log_rename(folder_path, filename, new_name)
                renamed_count += 1
            except Exception as e:
                messagebox.showerror("错误", f"重命名失败：{filename} -> {new_name}\n{e}")

        if not include_subdirs:
            break

    messagebox.showinfo("完成", f"成功重命名 {renamed_count} 个文件！")

# 配置替换规则窗口
def configure_replacement_rules():
    def add_rule():
        old = old_entry.get()
        new = new_entry.get()
        if old:
            replacement_rules.append((old, new))
            rules_listbox.insert("end", f"{old} -> {new}")
            old_entry.delete(0, "end")
            new_entry.delete(0, "end")

    def remove_rule():
        selected = rules_listbox.curselection()
        if selected:
            replacement_rules.pop(selected[0])
            rules_listbox.delete(selected[0])

    rules_window = Toplevel(root)
    rules_window.title("配置替换规则")
    rules_window.geometry("400x300")

    Label(rules_window, text="原字符串:").grid(row=0, column=0, padx=5, pady=5)
    old_entry = Entry(rules_window)
    old_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(rules_window, text="新字符串:").grid(row=1, column=0, padx=5, pady=5)
    new_entry = Entry(rules_window)
    new_entry.grid(row=1, column=1, padx=5, pady=5)

    Button(rules_window, text="添加", command=add_rule).grid(row=2, column=0, padx=5, pady=5)
    Button(rules_window, text="删除", command=remove_rule).grid(row=2, column=1, padx=5, pady=5)

    rules_listbox = Listbox(rules_window, width=50, height=10)
    rules_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# 文件名预览窗口
def preview_rename():
    folder_path = folder_path_entry.get()

    if not folder_path:
        messagebox.showerror("错误", "请选择文件夹！")
        return

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        messagebox.showerror("错误", "输入的文件夹路径无效！")
        return

    preview_window = Toplevel(root)
    preview_window.title("文件重命名预览")
    preview_window.geometry("500x400")

    Label(preview_window, text="文件名预览：").grid(row=0, column=0, padx=10, pady=10)

    listbox = Listbox(preview_window, width=60, height=15)
    listbox.grid(row=1, column=0, padx=10, pady=10)

    for root_dir, _, filenames in os.walk(folder_path):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            student_id, student_name = extract_student_info(name)
            if student_id and student_name:
                new_name = student_id + student_name + ext
            else:
                new_name = name + ext

            # 应用替换规则
            for old, new in replacement_rules:
                new_name = new_name.replace(old, new)

            # 插入文本
            if insert_text_var.get():
                insert_position = int(insert_position_var.get() or 0)
                insert_text = insert_text_entry.get()
                if 0 <= insert_position < len(new_name):
                    new_name = new_name[:insert_position] + insert_text + new_name[insert_position:]

            # 移除指定字符
            if remove_text_var.get():
                chars_to_remove = remove_text_entry.get()
                for char in chars_to_remove:
                    new_name = new_name.replace(char, "")

            # 保留指定字符（移除其他字符）
            if retain_text_var.get():
                chars_to_retain = retain_text_entry.get()
                new_name = "".join([c for c in new_name if c in chars_to_retain]) + ext

            listbox.insert("end", f"{filename} -> {new_name}")

    Button(preview_window, text="关闭", command=preview_window.destroy).grid(row=2, column=0, padx=10, pady=10)

# GUI 主窗口
root = Tk()
root.title("批量重命名工具")
root.geometry("700x500")
root.resizable(False, False)

replacement_rules = []

Label(root, text="选择文件夹：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
folder_path_entry = Entry(root, width=40)
folder_path_entry.grid(row=0, column=1, padx=10, pady=10)
Button(root, text="浏览", command=lambda: folder_path_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=10, pady=10)

subdir_var = IntVar()
Checkbutton(root, text="包含子目录", variable=subdir_var).grid(row=1, column=1, padx=10, pady=10, sticky="w")

log_var = IntVar()
Checkbutton(root, text="记录重命名日志", variable=log_var).grid(row=2, column=1, padx=10, pady=10, sticky="w")

insert_text_var = IntVar()
Checkbutton(root, text="插入文本", variable=insert_text_var).grid(row=3, column=0, padx=10, pady=10, sticky="w")
insert_text_entry = Entry(root)
insert_text_entry.grid(row=3, column=1, padx=10, pady=10)
insert_position_var = StringVar()
insert_position_entry = Entry(root, textvariable=insert_position_var, width=10)
insert_position_entry.grid(row=3, column=2, padx=10, pady=10)

remove_text_var = IntVar()
Checkbutton(root, text="移除指定字符", variable=remove_text_var).grid(row=4, column=0, padx=10, pady=10, sticky="w")
remove_text_entry = Entry(root)
remove_text_entry.grid(row=4, column=1, padx=10, pady=10)

retain_text_var = IntVar()
Checkbutton(root, text="保留指定字符", variable=retain_text_var).grid(row=5, column=0, padx=10, pady=10, sticky="w")
retain_text_entry = Entry(root)
retain_text_entry.grid(row=5, column=1, padx=10, pady=10)

Button(root, text="配置替换规则", command=configure_replacement_rules, bg="lightyellow").grid(row=6, column=1, pady=10)
Button(root, text="预览", command=preview_rename, bg="lightblue").grid(row=7, column=1, pady=10)
Button(root, text="开始重命名", command=rename_files, bg="lightgreen").grid(row=8, column=1, pady=20)

root.mainloop()
