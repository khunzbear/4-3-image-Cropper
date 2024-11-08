import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

def crop_and_add_text(image_path, text, font_path, target_ratio=(4, 3), crop_margin=0.0):
    with Image.open(image_path) as img:
        width, height = img.size
        current_ratio = width / height
        target_width, target_height = target_ratio
        target_ratio_value = target_width / target_height

        # คำนวณขนาดที่ตัดออกตามอัตราส่วนที่ผู้ใช้กำหนด
        if current_ratio > target_ratio_value:
            new_width = int(height * target_ratio_value)
            left = (width - new_width) // 2
            right = left + new_width
            top, bottom = 0, height
        else:
            new_height = int(width / target_ratio_value)
            top = (height - new_height) // 2
            bottom = top + new_height
            left, right = 0, width
        
        # ตัดขอบตามค่าที่ผู้ใช้เลือก
        width_to_crop = int((right - left) * crop_margin)  # กำหนดขนาดขอบที่ตัด
        height_to_crop = int((bottom - top) * crop_margin)
        
        # ใช้ตัวเลือก crop margin
        left += width_to_crop
        right -= width_to_crop
        top += height_to_crop
        bottom -= height_to_crop

        img_cropped = img.crop((left, top, right, bottom))

        draw = ImageDraw.Draw(img_cropped)
        
        try:
            font = ImageFont.truetype(font_path, 16)  # ใช้ฟอนต์ที่เลือก
        except IOError:
            output_label.config(text="ไม่สามารถโหลดฟอนต์นี้ได้")
            return None
        
        # ใช้ textbbox เพื่อคำนวณขนาดข้อความ
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        
        # กำหนดตำแหน่งที่มุมขวาล่างโดยมีขอบเล็กน้อย
        x = img_cropped.width - text_width - 10
        y = img_cropped.height - text_height - 20

        draw.text((x, y), text, font=font, fill="white")  # ข้อความจริง

        return img_cropped

def browse_image():
    global image_paths
    image_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if image_paths:
        image_list_label.config(text=f"Selected {len(image_paths)} images.")

def browse_font():
    global font_path
    font_path = filedialog.askopenfilename(filetypes=[("Font Files", "*.ttf;*.otf")])
    if font_path:
        font_label.config(text=f"Selected Font: {font_path}")

def preview_image(image_path, text, crop_margin):
    if image_path and text and font_path:
        # โหลดและแสดงภาพที่ตัดและเพิ่มข้อความ
        img_preview = crop_and_add_text(image_path, text, font_path, crop_margin=crop_margin)
        if img_preview:
            img_preview.thumbnail((250, 250))
            img_display = ImageTk.PhotoImage(img_preview)
            preview_label.config(image=img_display)
            preview_label.image = img_display
            preview_label.config(text="Preview")

def process_images():
    text = text_entry.get()
    crop_margin = crop_margin_scale.get() / 100.0  # อ่านค่าจาก slider และแปลงเป็นเปอร์เซ็นต์
    if image_paths and text and font_path:
        # เลือกโฟลเดอร์ที่จะบันทึกไฟล์ output
        output_dir = filedialog.askdirectory()
        if output_dir:
            for idx, image_path in enumerate(image_paths):
                output_filename = f"{idx+1:03d}_output.jpg"  # ตั้งชื่อไฟล์เป็นลำดับ เช่น 001_output.jpg
                output_path = os.path.join(output_dir, output_filename)
                
                # ตรวจสอบและทำการตัดและเพิ่มข้อความ
                img_cropped = crop_and_add_text(image_path, text, font_path, crop_margin=crop_margin)
                
                if img_cropped:
                    # บันทึกภาพ
                    img_cropped.save(output_path)

                    # แสดงข้อความว่าบันทึกภาพแล้ว
                    output_label.config(text=f"Processed Image {idx+1} Saved as '{output_filename}'")
                else:
                    output_label.config(text="Error processing image.")

def show_about():
    about_window = tk.Toplevel(app)
    about_window.title("About")
    about_label = tk.Label(about_window, text="This app was developed by Khunnatham Suwannarin\n khun.suwan16@gmail.com")
    about_label.pack(pady=20)
    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack(pady=10)

app = tk.Tk()
app.title("4:3 Image Cropper")

# ให้หน้าต่างสามารถขยายและปรับขนาดได้
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

image_paths = []
font_path = None

# ปุ่มเลือกฟอนต์
browse_font_button = tk.Button(app, text="เลือกไฟล์ฟอนต์", command=browse_font)
browse_font_button.grid(row=0, column=0, pady=10, padx=10)

font_label = tk.Label(app, text="ยังไม่ได้เลือกฟอนต์")
font_label.grid(row=1, column=0, pady=5)

browse_button = tk.Button(app, text="ค้นหารูป", command=browse_image)
browse_button.grid(row=2, column=0, pady=10, padx=10)

image_list_label = tk.Label(app, text="ยังไม่ได้เลือกรูปภาพ")
image_list_label.grid(row=3, column=0, pady=5)

# พื้นที่กรอกข้อความ
tk.Label(app, text="ข้อความ").grid(row=4, column=0)
text_entry = tk.Entry(app)
text_entry.grid(row=5, column=0, pady=5)

# Slider ให้เลือกขนาดขอบที่ต้องการตัด
tk.Label(app, text="เลือกขนาดการตัดขอบ (%)").grid(row=6, column=0, pady=5)
crop_margin_scale = tk.Scale(app, from_=0, to=50, orient="horizontal")
crop_margin_scale.set(0)
crop_margin_scale.grid(row=7, column=0, pady=5)

# ปุ่มดูตัวอย่าง
preview_button = tk.Button(app, text="ดูตัวอย่างรูป", command=lambda: preview_image(image_paths[0], text_entry.get(), crop_margin_scale.get() / 100.0) if image_paths else None)
preview_button.grid(row=8, column=0, pady=10)

preview_label = tk.Label(app, text="Preview")
preview_label.grid(row=9, column=0, pady=10)

process_button = tk.Button(app, text="บันทึก", command=process_images)
process_button.grid(row=10, column=0, pady=10)

output_label = tk.Label(app, text="")
output_label.grid(row=11, column=0, pady=10)

about_button = tk.Button(app, text="About", command=show_about)
about_button.grid(row=12, column=0, pady=10)

app.mainloop()
