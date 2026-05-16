import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ImageStitcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Image Stitcher by mhhhoa")
        self.geometry("1300x900")
        self.after(201, lambda: self.iconbitmap(default="")) 

        self.images =[] 
        self.zoom_factor = 1.0 

        # Библиотека Pantone
        self.color_palette = {
            "White": "#FFFFFF", "Black": "#000000", "Viva Magenta": "#BE3455",
            "Flame": "#FF4C30", "Peach Fuzz": "#FFBE98", "Illuminating": "#F5DF4D",
            "Cyber Lime": "#DAFF01", "Kelly Green": "#4CBB17", "Classic Blue": "#0F4C81",
            "Very Peri": "#6667AB", "Digital Lavender": "#B57EDC", "Radiant Orchid": "#AD5E99"
        }

        self.font_map = {
            "Arial": "arial.ttf", "Verdana": "verdana.ttf",
            "Times New Roman": "times.ttf", "Georgia": "georgia.ttf",
            "Courier New": "cour.ttf", "Impact": "impact.ttf"
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- ЛЕВАЯ ПАНЕЛЬ (Sidebar) ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=360, corner_radius=0, fg_color="#1e1e1e")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # ЛОГОТИП
        ctk.CTkLabel(self.sidebar, text="SMART STITCHER", font=("Impact", 28), text_color="#3a7ebf").pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text="by mhhhoa", font=("Arial", 12), text_color="#555555").pack(pady=(0, 20))

        # --- ГРУППА: ПАРАМЕТРЫ И ДИЗАЙН ---
        self.group_settings = self.create_group("ПАРАМЕТРЫ И ДИЗАЙН")
        
        ctk.CTkLabel(self.group_settings, text="Направление:").pack(anchor="w", padx=10, pady=(5,0))
        self.direction_menu = ctk.CTkOptionMenu(self.group_settings, values=["Горизонтально", "Вертикально"], command=self.trigger_preview)
        self.direction_menu.set("Горизонтально")
        self.direction_menu.pack(pady=5, fill="x", padx=10)

        ctk.CTkLabel(self.group_settings, text="Отступ (px):").pack(anchor="w", padx=10, pady=(10,0))
        self.pad_container = ctk.CTkFrame(self.group_settings, fg_color="transparent")
        self.pad_container.pack(pady=(5, 5), fill="x", padx=10) 
        self.padding_slider = ctk.CTkSlider(self.pad_container, from_=0, to=100, command=self.update_padding_slider)
        self.padding_slider.set(15)
        self.padding_slider.pack(side="left", fill="x", expand=True)
        self.padding_entry = ctk.CTkEntry(self.pad_container, width=45, height=25)
        self.padding_entry.insert(0, "15")
        self.padding_entry.pack(side="right", padx=(5,0))
        self.padding_entry.bind("<Return>", self.update_padding_entry)

        ctk.CTkLabel(self.group_settings, text="Цвет разделителя:").pack(anchor="w", padx=10, pady=(10,0))
        self.bg_row = ctk.CTkFrame(self.group_settings, fg_color="transparent")
        self.bg_row.pack(fill="x", padx=10, pady=(5, 5))
        self.bg_color_preview = ctk.CTkFrame(self.bg_row, width=20, height=20, corner_radius=10, fg_color="#FFFFFF", border_width=1)
        self.bg_color_preview.pack(side="left", padx=(0, 10))
        self.bg_color_menu = ctk.CTkOptionMenu(self.bg_row, values=list(self.color_palette.keys()) +["Transparent (only PNG)"], command=self.trigger_preview)
        self.bg_color_menu.set("White")
        self.bg_color_menu.pack(side="left", fill="x", expand=True)

        self.border_switch = ctk.CTkSwitch(self.group_settings, text="Добавить рамку", command=self.trigger_preview)
        self.border_switch.pack(pady=10, anchor="w", padx=10)

        self.corner_switch = ctk.CTkSwitch(self.group_settings, text="Закруглить края фото", command=self.trigger_preview)
        self.corner_switch.pack(pady=(0, 10), anchor="w", padx=10)

        # --- ГРУППА: ТЕКСТ И МАРКИРОВКА ---
        self.group_labels = self.create_group("ТЕКСТ И МАРКИРОВКА")
        self.label_switch = ctk.CTkSwitch(self.group_labels, text="Надписи ДО / ПОСЛЕ", command=self.toggle_label_options)
        self.label_switch.pack(pady=(10, 15), anchor="w", padx=10)

        self.label_options_frame = ctk.CTkFrame(self.group_labels, fg_color="transparent")
        self.setup_label_ui()

        # --- ГРУППА: ЭКСПОРТ ---
        self.group_export = self.create_group("ЭКСПОРТ")

        # Было: pady=10
        # Стало: pady=(10, 5) -> 10 сверху, 5 снизу
        ctk.CTkLabel(self.group_export, text="Формат:").pack(side="left", padx=10, pady=(1, 10))

        self.format_menu = ctk.CTkOptionMenu(self.group_export, values=["JPG", "PNG"], width=100)
        self.format_menu.set("JPG")

        # Тоже меняем нижний отступ
        self.format_menu.pack(side="right", padx=10, pady=(0, 10))

        # КНОПКА СОХРАНЕНИЯ
        self.btn_save = ctk.CTkButton(self.sidebar, text="СОХРАНИТЬ РЕЗУЛЬТАТ", command=self.save_result, 
                                      fg_color="#2eb85c", hover_color="#1e7a3d", height=50, font=("Arial", 16, "bold"))
        self.btn_save.pack(pady=30, padx=20, fill="x")

        # --- ПРАВАЯ ПАНЕЛЬ (Превью) ---
        self.preview_frame = ctk.CTkFrame(self, fg_color="#121212")
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.btn_add = ctk.CTkButton(self.preview_frame, text="+ Добавить файлы", command=self.add_images, 
                                     fg_color="#3a7ebf", hover_color="#2d5a8a", height=40)
        self.btn_add.pack(pady=20)

        self.image_container = ctk.CTkLabel(self.preview_frame, text="Перетащите или добавьте файлы, \nчтобы начать создание коллажа", 
                                            text_color="#444444", font=("Arial", 18), pady=20)
        self.image_container.pack(expand=True, fill="both", padx=20)

        # --- ПЛАВАЮЩИЙ ЗУМ ---
        self.zoom_bar = ctk.CTkFrame(self.preview_frame, fg_color="#2b2b2b", corner_radius=25, border_width=1, border_color="#444444")
        self.zoom_bar.place(relx=0.5, rely=0.95, anchor="s")

        z_btn_style = {"width": 30, "height": 30, "fg_color": "transparent", "hover_color": "#404040", "corner_radius": 15, "text_color": "#ffffff"}

        ctk.CTkButton(self.zoom_bar, text="−", **z_btn_style, command=self.zoom_out).pack(side="left", padx=(10, 5), pady=5)
        self.zoom_label = ctk.CTkLabel(self.zoom_bar, text="100%", font=("Arial", 12, "bold"), width=50)
        self.zoom_label.pack(side="left", pady=5)
        ctk.CTkButton(self.zoom_bar, text="+", **z_btn_style, command=self.zoom_in).pack(side="left", padx=(5, 5), pady=5)

        ctk.CTkFrame(self.zoom_bar, width=1, height=20, fg_color="#444444").pack(side="left", padx=5)

        ctk.CTkButton(self.zoom_bar, text="1:1", width=45, height=30, fg_color="transparent", 
                      hover_color="#404040", corner_radius=15, font=("Arial", 11, "bold"), 
                      command=self.zoom_reset).pack(side="left", padx=(5, 10), pady=5)

        self.btn_clear = ctk.CTkButton(self.preview_frame, text="Очистить всё", fg_color="transparent", 
                                       text_color="#888888", hover_color="#333333", command=self.clear_all, width=100)
        self.btn_clear.pack(pady=(0, 15)) 

        self.bind_all("<Control-MouseWheel>", self.on_mouse_zoom)

    # --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
    def create_group(self, title):
        frame = ctk.CTkFrame(self.sidebar, fg_color="#252525", corner_radius=10, border_width=1, border_color="#333333")
        frame.pack(fill="x", padx=15, pady=10)
        # Изменили pady=(8, 0) — убрали лишнее место под заголовком
        label = ctk.CTkLabel(frame, text=title, font=("Arial", 11, "bold"), text_color="#777777")
        label.pack(pady=(8, 0), padx=10, anchor="w")
        return frame

    def setup_label_ui(self):
        ctk.CTkLabel(self.label_options_frame, text="Язык / Регистр:").pack(anchor="w", padx=10)
        row1 = ctk.CTkFrame(self.label_options_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10)
        self.lang_menu = ctk.CTkOptionMenu(row1, values=["Русский", "English"], command=self.trigger_preview, height=25)
        self.lang_menu.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.case_menu = ctk.CTkOptionMenu(row1, values=["CAPS LOCK", "Первая заглавная", "строчные"], command=self.trigger_preview, height=25)
        self.case_menu.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(self.label_options_frame, text="Шрифт / Цвет:").pack(anchor="w", padx=10, pady=(10,0))
        row2 = ctk.CTkFrame(self.label_options_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10)
        self.font_menu = ctk.CTkOptionMenu(row2, values=list(self.font_map.keys()), command=self.trigger_preview, height=25)
        self.font_menu.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.text_color_preview = ctk.CTkFrame(row2, width=20, height=20, corner_radius=10, fg_color="#000000", border_width=1)
        self.text_color_preview.pack(side="left", padx=5)
        self.text_color_menu = ctk.CTkOptionMenu(row2, values=list(self.color_palette.keys()), command=self.trigger_preview, height=25, width=100)
        self.text_color_menu.set("Black")
        self.text_color_menu.pack(side="left")

        ctk.CTkLabel(self.label_options_frame, text="Размер надписи (%):").pack(anchor="w", padx=10, pady=(10,0))
        row3 = ctk.CTkFrame(self.label_options_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 15)) 
        self.text_size_slider = ctk.CTkSlider(row3, from_=1, to=30, command=self.update_text_size_slider)
        self.text_size_slider.set(10)
        self.text_size_slider.pack(side="left", fill="x", expand=True)
        self.text_size_entry = ctk.CTkEntry(row3, width=40, height=25)
        self.text_size_entry.insert(0, "10")
        self.text_size_entry.pack(side="right", padx=(5,0))
        self.text_size_entry.bind("<Return>", self.update_text_size_entry)

        ctk.CTkLabel(self.label_options_frame, text="Выравнивание:").pack(anchor="w", padx=10)
        self.text_align_menu = ctk.CTkOptionMenu(self.label_options_frame, values=["Слева", "Центр", "Справа"], command=self.trigger_preview)
        self.text_align_menu.set("Слева")
        self.text_align_menu.pack(fill="x", padx=10, pady=(0, 10))

    def toggle_label_options(self):
        if self.label_switch.get(): self.label_options_frame.pack(fill="x", pady=5)
        else: self.label_options_frame.pack_forget()
        self.trigger_preview()

    def update_text_size_slider(self, val):
        self.text_size_entry.delete(0, "end"); self.text_size_entry.insert(0, str(int(val)))
        self.update_preview()

    def update_text_size_entry(self, event):
        try:
            val = int(self.text_size_entry.get())
            if 1 <= val <= 30: self.text_size_slider.set(val); self.update_preview()
        except: pass

    def update_padding_slider(self, val):
        self.padding_entry.delete(0, "end"); self.padding_entry.insert(0, str(int(val)))
        self.update_preview()

    def update_padding_entry(self, event):
        try:
            val = int(self.padding_entry.get())
            if 0 <= val <= 100: self.padding_slider.set(val); self.update_preview()
        except: pass

    def trigger_preview(self, *args):
        bg_col = self.bg_color_menu.get()
        self.bg_color_preview.configure(fg_color=self.color_palette.get(bg_col, "transparent"))
        txt_col = self.text_color_menu.get()
        self.text_color_preview.configure(fg_color=self.color_palette.get(txt_col, "#000000"))
        self.update_preview()

    def add_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if files:
            for f in files: self.images.append(Image.open(f).convert("RGBA"))
            self.update_preview()

    def clear_all(self):
        self.images =[]; self.zoom_factor = 1.0
        self.image_container.configure(image="", text="Перетащите или добавьте файлы, \nчтобы начать создание коллажа")
        self.zoom_label.configure(text="100%")

    def on_mouse_zoom(self, event):
        if event.delta > 0: self.zoom_in()
        else: self.zoom_out()

    def zoom_in(self, event=None):
        if self.images: self.zoom_factor *= 1.2; self.update_preview()

    def zoom_out(self, event=None):
        if self.images:
            self.zoom_factor /= 1.2
            if self.zoom_factor < 0.1: self.zoom_factor = 0.1
            self.update_preview()

    def zoom_reset(self):
        self.zoom_factor = 1.0; self.update_preview()

    def add_corners(self, im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im

    def draw_smart_label(self, canvas, idx, box_x, box_y, box_w, box_h):
        draw = ImageDraw.Draw(canvas)
        raw_text = ("ДО" if idx == 0 else "ПОСЛЕ") if self.lang_menu.get() == "Русский" else ("BEFORE" if idx == 0 else "AFTER")
        case_mode = self.case_menu.get()
        if case_mode == "Первая заглавная": final_text = raw_text.capitalize()
        elif case_mode == "строчные": final_text = raw_text.lower()
        else: final_text = raw_text.upper() # CAPS LOCK

        font_size = int(box_h * (self.text_size_slider.get() / 100))
        if font_size < 10: font_size = 10
        font_file = self.font_map.get(self.font_menu.get(), "arial.ttf")
        try: font = ImageFont.truetype(font_file, font_size)
        except: font = ImageFont.load_default()

        text_color = self.color_palette.get(self.text_color_menu.get(), "#000000")
        align = self.text_align_menu.get()
        text_bbox = draw.textbbox((0, 0), final_text, font=font)
        tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        
        margin = 30
        if align == "Слева": tx = box_x + margin
        elif align == "Центр": tx = box_x + (box_w - tw) // 2
        else: tx = box_x + box_w - tw - margin
        
        draw.text((tx, box_y + margin), final_text, fill=text_color, font=font)

    def create_collage(self, is_preview=True):
        if not self.images: return None
        direction = self.direction_menu.get(); padding = int(self.padding_slider.get())
        color_name = self.bg_color_menu.get()
        source_images = [img.copy() for img in self.images]
        
        if is_preview:
            for img in source_images: img.thumbnail((1200, 1200))
            
        border_offset = padding if self.border_switch.get() else 0
            
        if direction == "Горизонтально":
            min_h = min(img.height for img in source_images)
            resized =[img.resize((int(img.width * (min_h / img.height)), min_h), Image.LANCZOS) for img in source_images]
            total_w = sum(i.width for i in resized) + (padding * (len(resized)-1)) + (border_offset * 2)
            total_h = min_h + (border_offset * 2)
        else:
            min_w = min(img.width for img in source_images)
            resized =[img.resize((min_w, int(img.height * (min_w / img.width))), Image.LANCZOS) for img in source_images]
            total_w = min_w + (border_offset * 2)
            total_h = sum(i.height for i in resized) + (padding * (len(resized)-1)) + (border_offset * 2)
            
        if self.corner_switch.get():
            radius = int(min(min_h if direction == "Горизонтально" else min_w, 200) * 0.05)
            resized =[self.add_corners(img, radius) for img in resized]
            
        bg_color = (0,0,0,0) if color_name == "Transparent" else self.color_palette.get(color_name, "#FFFFFF")
        canvas = Image.new("RGBA", (total_w, total_h), color=bg_color)
        
        current_pos = border_offset
        for i, img in enumerate(resized):
            if direction == "Горизонтально":
                canvas.alpha_composite(img, (current_pos, border_offset))
                if self.label_switch.get() and i < 2: 
                    self.draw_smart_label(canvas, i, current_pos, border_offset, img.width, img.height)
                current_pos += img.width + padding
            else:
                canvas.alpha_composite(img, (border_offset, current_pos))
                if self.label_switch.get() and i < 2: 
                    self.draw_smart_label(canvas, i, border_offset, current_pos, img.width, img.height)
                current_pos += img.height + padding
        return canvas

    def update_preview(self):
        if not self.images: return
        collage = self.create_collage(is_preview=True)
        if collage:
            win_w = self.preview_frame.winfo_width() - 80
            win_h = self.preview_frame.winfo_height() - 220
            if win_w < 100: win_w, win_h = 900, 600
            ratio = min(win_w/collage.width, win_h/collage.height)
            final_w = int(collage.width * ratio * self.zoom_factor)
            final_h = int(collage.height * ratio * self.zoom_factor)
            collage = collage.resize((final_w, final_h), Image.LANCZOS)
            self.ctk_img = ctk.CTkImage(light_image=collage, dark_image=collage, size=(final_w, final_h))
            self.image_container.configure(image=self.ctk_img, text="")
            self.zoom_label.configure(text=f"{int(self.zoom_factor * 100)}%")

    def save_result(self):
        if not self.images: return
        fmt = self.format_menu.get()
        save_path = filedialog.asksaveasfilename(defaultextension=f".{fmt.lower()}")
        if save_path:
            final = self.create_collage(is_preview=False)
            if fmt == "JPG": final = final.convert("RGB")
            final.save(save_path, quality=95 if fmt == "JPG" else None)
            messagebox.showinfo("Успех", "Коллаж сохранен!")

if __name__ == "__main__":
    app = ImageStitcherApp()
    app.after(250, app.trigger_preview)
    app.mainloop()