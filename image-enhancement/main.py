import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from enhancement import enhance_image


class ImageEnhancementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Enhancement Studio")
        self.root.geometry("1250x850")
        self.root.minsize(950, 700)
        self.root.configure(bg="#151b27")

        self.bg = "#151b27"
        self.panel = "#202b3b"
        self.panel_dark = "#111827"
        self.accent = "#3b82f6"
        self.text_color = "#f1f5f9"
        self.muted = "#94a3b8"

        self.original_image = None
        self.enhanced_image = None
        self.image_path = None

        self.grayscale = tk.BooleanVar(value=False)
        self.denoise = tk.BooleanVar(value=False)
        self.histogram = tk.BooleanVar(value=False)

        # Undo stores complete enhancement settings, not image copies.
        self.history = []
        self.max_history = 50
        self.drag_start_state = None
        self.restoring = False
        self.preview_photo_original = None
        self.preview_photo_enhanced = None

        self._build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=24, pady=(14, 5))

        tk.Label(
            header,
            text="✦  IMAGE ENHANCEMENT STUDIO",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg,
            fg=self.text_color
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Improve your images with intelligent processing techniques",
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.muted
        ).pack(anchor="w", pady=(3, 0))

        # Toolbar
        toolbar = tk.Frame(self.root, bg=self.bg)
        toolbar.pack(fill="x", padx=24, pady=8)

        self._button(toolbar, "📂  Upload Image", self.upload_image,
                     self.accent).pack(side="left", padx=(0, 8))
        self.undo_button = self._button(
            toolbar, "↶  Undo", self.undo, "#475569"
        )
        self.undo_button.pack(side="left", padx=5)
        self.undo_button.config(state="disabled")
        self._button(toolbar, "⟲  Reset", self.reset_image,
                     "#d97706").pack(side="left", padx=5)
        self._button(toolbar, "⬇  Save Image", self.save_image,
                     "#15803d").pack(side="right")

        # Image information
        info = tk.LabelFrame(
            self.root,
            text="  IMAGE INFORMATION  ",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.text_color,
            padx=10,
            pady=7
        )
        info.pack(fill="x", padx=24, pady=6)

        self.info_labels = {}
        info_items = [
            ("Width", "width"), ("Height", "height"),
            ("Format", "format"), ("File Size", "size"),
            ("Channels", "channels"), ("Total Pixels", "pixels")
        ]

        for col, (caption, key) in enumerate(info_items):
            cell = tk.Frame(info, bg=self.panel)
            cell.grid(row=0, column=col, sticky="w", padx=12, pady=2)
            tk.Label(
                cell, text=caption, bg=self.panel, fg=self.muted,
                font=("Segoe UI", 9)
            ).pack(anchor="w")
            value = tk.Label(
                cell, text="--", bg=self.panel, fg="#60a5fa",
                font=("Segoe UI", 10, "bold")
            )
            value.pack(anchor="w", pady=(2, 0))
            self.info_labels[key] = value
            info.grid_columnconfigure(col, weight=1)

        # Enhancement controls are deliberately ABOVE the preview panels
        controls = tk.LabelFrame(
            self.root,
            text="  IMAGE ENHANCEMENT CONTROLS  ",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.text_color,
            padx=12,
            pady=7
        )
        controls.pack(fill="x", padx=24, pady=6)

        slider_row = tk.Frame(controls, bg=self.panel)
        slider_row.pack(fill="x")

        self.brightness_slider = self._create_slider(
            slider_row, "☀  Brightness", -100, 100
        )
        self.contrast_slider = self._create_slider(
            slider_row, "◐  Contrast", -100, 100
        )
        self.sharpness_slider = self._create_slider(
            slider_row, "✧  Sharpness", 0, 100
        )

        options = tk.Frame(controls, bg=self.panel)
        options.pack(fill="x", pady=(3, 0))

        self._create_checkbox(options, "Grayscale", self.grayscale)
        self._create_checkbox(options, "Noise Reduction", self.denoise)
        self._create_checkbox(
            options, "Histogram Equalization", self.histogram
        )

        # Side-by-side image comparison
        preview_container = tk.Frame(self.root, bg=self.bg)
        preview_container.pack(
            fill="both", expand=True, padx=24, pady=(5, 8)
        )

        self.original_label = self._create_preview_panel(
            preview_container, "01  ORIGINAL IMAGE",
            "Upload an image to begin"
        )
        self.enhanced_label = self._create_preview_panel(
            preview_container, "02  ENHANCED IMAGE",
            "Your enhanced image appears here"
        )

        # Status bar
        self.status = tk.Label(
            self.root,
            text="● Ready | Please upload an image",
            bg="#101722",
            fg="#93c5fd",
            font=("Segoe UI", 9),
            anchor="w",
            padx=20,
            pady=7
        )
        self.status.pack(fill="x", side="bottom")

    def _button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=13,
            pady=8
        )

    def _create_slider(self, parent, title, minimum, maximum):
        frame = tk.Frame(parent, bg=self.panel)
        frame.pack(side="left", fill="x", expand=True, padx=8)

        tk.Label(
            frame, text=title, bg=self.panel, fg=self.text_color,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        slider = tk.Scale(
            frame,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            command=self.update_image,
            bg=self.panel,
            fg="white",
            troughcolor="#334155",
            activebackground=self.accent,
            highlightthickness=0,
            showvalue=True,
            resolution=1,
            sliderlength=18,
            length=250
        )
        slider.set(0)
        slider.pack(fill="x")

        # Capture the settings from before a slider drag for one-step undo.
        slider.bind("<ButtonPress-1>", self._begin_slider_change)
        slider.bind("<ButtonRelease-1>", self._finish_slider_change)
        return slider

    def _create_checkbox(self, parent, title, variable):
        tk.Checkbutton(
            parent,
            text=title,
            variable=variable,
            command=self._checkbox_changed,
            bg=self.panel,
            fg=self.text_color,
            selectcolor="#334155",
            activebackground=self.panel,
            activeforeground="white",
            font=("Segoe UI", 9),
            cursor="hand2"
        ).pack(side="left", padx=(8, 22))

    def _create_preview_panel(self, parent, title, placeholder):
        frame = tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.text_color,
            padx=8,
            pady=8
        )
        frame.pack(side="left", fill="both", expand=True, padx=6)

        label = tk.Label(
            frame,
            text=placeholder,
            bg=self.panel_dark,
            fg=self.muted,
            font=("Segoe UI", 10)
        )
        label.pack(fill="both", expand=True)
        return label

    # ---------------------------------------------------------
    # State and undo
    # ---------------------------------------------------------
    def _current_settings(self):
        return {
            "brightness": int(self.brightness_slider.get()),
            "contrast": int(self.contrast_slider.get()),
            "sharpness": int(self.sharpness_slider.get()),
            "grayscale": bool(self.grayscale.get()),
            "denoise": bool(self.denoise.get()),
            "histogram": bool(self.histogram.get())
        }

    def _push_history(self, state):
        if state is None:
            return
        if self.history and self.history[-1] == state:
            return
        self.history.append(state.copy())
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self._refresh_undo_button()

    def _refresh_undo_button(self):
        self.undo_button.config(
            state="normal" if self.history else "disabled"
        )

    def _begin_slider_change(self, event=None):
        if self.original_image is not None and not self.restoring:
            self.drag_start_state = self._current_settings()

    def _finish_slider_change(self, event=None):
        if self.drag_start_state is not None:
            current = self._current_settings()
            if current != self.drag_start_state:
                self._push_history(self.drag_start_state)
            self.drag_start_state = None
            self._refresh_undo_button()

    def _checkbox_changed(self):
        if self.original_image is None or self.restoring:
            return
        # The checkbox command is called after Tk has changed its variable.
        # The previous state is reconstructed from the last applied settings.
        previous = self.last_applied_settings.copy()
        self._push_history(previous)
        self.update_image()

    def undo(self):
        if self.original_image is None or not self.history:
            return

        state = self.history.pop()
        self._apply_settings(state)
        self._refresh_undo_button()
        self._render_enhanced_image()
        self.status.config(text="● Previous enhancement restored")

    def _apply_settings(self, state):
        self.restoring = True
        self.brightness_slider.set(state["brightness"])
        self.contrast_slider.set(state["contrast"])
        self.sharpness_slider.set(state["sharpness"])
        self.grayscale.set(state["grayscale"])
        self.denoise.set(state["denoise"])
        self.histogram.set(state["histogram"])
        self.restoring = False
        self.last_applied_settings = state.copy()

    # ---------------------------------------------------------
    # Image processing and display
    # ---------------------------------------------------------
    def update_image(self, value=None):
        if self.original_image is None or self.restoring:
            return

        settings = self._current_settings()
        self.enhanced_image = enhance_image(
            self.original_image,
            brightness=settings["brightness"],
            contrast=settings["contrast"],
            sharpness=settings["sharpness"],
            grayscale=settings["grayscale"],
            denoise=settings["denoise"],
            histogram=settings["histogram"]
        )
        self.last_applied_settings = settings.copy()
        self._render_enhanced_image()
        self.status.config(text="● Enhancement applied successfully")

    def _render_enhanced_image(self):
        if self.enhanced_image is not None:
            self._display_image(self.enhanced_image, self.enhanced_label)

    def _display_image(self, image, label, is_original=False):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)

        # Fit the image to the preview panel while preserving aspect ratio.
        max_width = max(label.winfo_width() - 20, 250)
        max_height = max(label.winfo_height() - 20, 180)
        pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(pil_image)
        label.config(image=photo, text="")
        if is_original:
            self.preview_photo_original = photo
        else:
            self.preview_photo_enhanced = photo

    def _display_both_images(self):
        if self.original_image is None:
            return
        self._display_image(
            self.original_image, self.original_label, is_original=True
        )
        self._display_image(self.enhanced_image, self.enhanced_label)

    def _refresh_previews_after_resize(self, event=None):
        if self.original_image is not None:
            self._display_both_images()

    # ---------------------------------------------------------
    # Upload and image information
    # ---------------------------------------------------------
    def upload_image(self):
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("All Files", "*.*")
            ]
        )
        if not path:
            return

        image = cv2.imread(path, cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror(
                "Image Error", "Unable to load the selected image."
            )
            return

        self.original_image = image
        self.enhanced_image = image.copy()
        self.image_path = path
        self.history.clear()
        self.drag_start_state = None

        self._set_default_controls()
        self.last_applied_settings = self._current_settings()
        self._update_information(path)

        self.root.update_idletasks()
        self._display_both_images()
        self._refresh_undo_button()
        self.status.config(
            text=f"● Uploaded: {os.path.basename(path)}"
        )

    def _update_information(self, path):
        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format or "Unknown"
            channels = len(img.getbands())

        file_size = os.path.getsize(path)
        if file_size < 1024 * 1024:
            size_text = f"{file_size / 1024:.2f} KB"
        else:
            size_text = f"{file_size / (1024 * 1024):.2f} MB"

        values = {
            "width": f"{width} px",
            "height": f"{height} px",
            "format": image_format,
            "size": size_text,
            "channels": str(channels),
            "pixels": f"{width * height:,}"
        }
        for key, value in values.items():
            self.info_labels[key].config(text=value)

    def _set_default_controls(self):
        self.restoring = True
        self.brightness_slider.set(0)
        self.contrast_slider.set(0)
        self.sharpness_slider.set(0)
        self.grayscale.set(False)
        self.denoise.set(False)
        self.histogram.set(False)
        self.restoring = False

    # ---------------------------------------------------------
    # Reset and save
    # ---------------------------------------------------------
    def reset_image(self):
        if self.original_image is None:
            messagebox.showwarning(
                "No Image", "Please upload an image first."
            )
            return

        current = self._current_settings()
        defaults = {
            "brightness": 0,
            "contrast": 0,
            "sharpness": 0,
            "grayscale": False,
            "denoise": False,
            "histogram": False
        }

        if current != defaults:
            self._push_history(current)

        self._apply_settings(defaults)
        self.enhanced_image = self.original_image.copy()
        self._display_both_images()
        self._refresh_undo_button()
        self.status.config(text="● Original image restored")

    def save_image(self):
        if self.enhanced_image is None:
            messagebox.showwarning(
                "No Image", "Please upload an image first."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Enhanced Image",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("BMP Image", "*.bmp")
            ]
        )
        if not path:
            return

        success = cv2.imwrite(path, self.enhanced_image)
        if success:
            messagebox.showinfo(
                "Saved", "Enhanced image saved successfully!"
            )
            self.status.config(
                text=f"● Saved: {os.path.basename(path)}"
            )
        else:
            messagebox.showerror(
                "Save Error", "Unable to save the image."
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancementApp(root)
    root.mainloop()
