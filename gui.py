import customtkinter as ctk
import tkinter.messagebox as mbox
from tkinter import filedialog
import threading
import os
import json
from win10toast import ToastNotifier
try:
    import downloader
except ImportError:
    downloader = None
    print('[ERRO] Módulo downloader não encontrado.')

from plyer import notification
import tkinter as tk
import requests
from io import BytesIO
from PIL import Image, ImageTk
import re

class YoutubeConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('YouTube Converter')
        self.iconbitmap('icone.ico')
        self.geometry('480x370')
        self.resizable(False, False)
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        self.is_dark = True

        self.configure(bg='#181c20')
        self.main_frame = ctk.CTkFrame(self, fg_color='#23272e', corner_radius=15)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Tema toggle
        self.theme_btn = ctk.CTkButton(self.main_frame, text='🌙', width=36, height=36, command=self.toggle_theme)
        self.theme_btn.place(relx=1, rely=0, anchor='ne', x=-10, y=10)

        self.url_label = ctk.CTkLabel(self.main_frame, text='URL do YouTube:', font=('Segoe UI', 14, 'bold'))
        self.url_label.pack(pady=(18, 2))
        self.url_entry = ctk.CTkEntry(self.main_frame, width=370, font=('Segoe UI', 12))
        self.url_entry.pack(pady=2)
        self.url_entry.configure(validate='key', validatecommand=(self.register(self.limit_url), '%P'))

        radio_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        radio_frame.pack(pady=10)
        self.format_var = ctk.StringVar(value='mp3')
        self.mp3_radio = ctk.CTkRadioButton(radio_frame, text='MP3', variable=self.format_var, value='mp3', font=('Segoe UI', 12))
        self.mp4_radio = ctk.CTkRadioButton(radio_frame, text='MP4', variable=self.format_var, value='mp4', font=('Segoe UI', 12))
        self.mp3_radio.pack(side='left', padx=20)
        self.mp4_radio.pack(side='left', padx=20)

        # Qualidade
        qual_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        qual_frame.pack(pady=2)
        self.qual_label = ctk.CTkLabel(qual_frame, text='Qualidade:', font=('Segoe UI', 12))
        self.qual_label.pack(side='left', padx=(0, 5))
        self.qual_var = ctk.StringVar(value='192')
        self.qual_menu = ctk.CTkOptionMenu(qual_frame, variable=self.qual_var, values=['128', '192', '320'], width=80)
        self.qual_menu.pack(side='left')

        dir_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        dir_frame.pack(pady=5)
        self.dir_label = ctk.CTkLabel(dir_frame, text='Salvar em:', font=('Segoe UI', 12))
        self.dir_label.pack(side='left', padx=(0, 5))
        self.dir_var = ctk.StringVar(value=os.getcwd())
        self.dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.dir_var, width=180, font=('Segoe UI', 11))
        self.dir_entry.pack(side='left', padx=5)
        self.dir_btn = ctk.CTkButton(dir_frame, text='Selecionar', command=self.select_dir, width=80, font=('Segoe UI', 11))
        self.dir_btn.pack(side='left', padx=5)

        self.progress = ctk.CTkProgressBar(self.main_frame, width=370, height=12, corner_radius=8, progress_color='#1e90ff')
        self.progress.set(0)
        self.progress.pack(pady=10)
        self.progress.pack_forget()

        self.status_label = ctk.CTkLabel(self.main_frame, text='', font=('Segoe UI', 11), text_color='#8fa1b3')
        self.status_label.pack(pady=2)

        self.download_btn = ctk.CTkButton(self.main_frame, text='Baixar', command=self.start_download, width=140, height=36, font=('Segoe UI', 14, 'bold'))
        self.download_btn.pack(pady=8)

        self.open_folder_btn = ctk.CTkButton(self.main_frame, text='Abrir Pasta', command=self.open_folder, width=120, height=32, font=('Segoe UI', 12))
        self.open_folder_btn.pack(pady=2)
        self.open_folder_btn.pack_forget()

        # Playlist
        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_check = ctk.CTkCheckBox(self.main_frame, text='Baixar playlist completa', variable=self.playlist_var, font=('Segoe UI', 11))
        self.playlist_check.pack(pady=2)

        # Detecta link na área de transferência
        self.after(500, self.check_clipboard_for_url)

        # Miniatura
        self.thumb_label = ctk.CTkLabel(self.main_frame, text='')
        self.thumb_label.pack(pady=(2, 2))
        self.thumb_img = None

        # Carregar configurações
        self.settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        settings = self.load_settings()
        self.settings = settings  # Salva no self para uso posterior

        # Tema personalizado (definir depois de carregar settings)
        self.theme_colors = {
            'Azul': {'theme': 'blue', 'color': '#1e90ff', 'entry_bg': '#23272e', 'label_fg': '#8fa1b3'},
            'Verde': {'theme': 'green', 'color': '#27ae60', 'entry_bg': '#23272e', 'label_fg': '#8fa1b3'},
            'Dark Blue': {'theme': 'dark-blue', 'color': '#34495e', 'entry_bg': '#23272e', 'label_fg': '#8fa1b3'}
        }
        self.theme_menu = ctk.CTkOptionMenu(self.main_frame, values=list(self.theme_colors.keys()), command=self.set_custom_theme)
        # Carregar tema salvo
        theme_to_set = self.settings.get('theme', 'Azul')
        if theme_to_set not in self.theme_colors:
            theme_to_set = 'Azul'
        self.theme_menu.set(theme_to_set)
        self.theme_menu.place(relx=0.01, rely=0.01, anchor='nw')

        # Criação dos widgets
        self.cancel_event = threading.Event()
        self.cancel_btn = ctk.CTkButton(self.main_frame, text='Cancelar', command=self.cancel_download, width=100, height=32, font=('Segoe UI', 12))
        self.cancel_btn.pack(pady=2)
        self.cancel_btn.pack_forget()

        # Só agora aplique o tema
        self.set_custom_theme(theme_to_set)
        # Carregar configurações restantes
        if self.settings.get('download_dir'):
            self.dir_var.set(self.settings['download_dir'])
        self.qual_var.set(self.settings.get('quality', '192'))
        # Corrigido: salvar settings no self para uso posterior
        self.settings = settings  # Salva no self para uso posterior

    def limit_url(self, value):
        return len(value) <= 200

    def toggle_theme(self):
        if self.is_dark:
            ctk.set_appearance_mode('light')
            self.theme_btn.configure(text='☀️')
        else:
            ctk.set_appearance_mode('dark')
            self.theme_btn.configure(text='🌙')
        self.is_dark = not self.is_dark

    def select_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_var.set(path)
            self.save_settings()

    def start_download(self):
        if downloader is None:
            mbox.showerror('Erro', 'Módulo downloader não encontrado!')
            return
        url = self.url_entry.get().strip()
        fmt = self.format_var.get()
        output_path = self.dir_var.get()
        qual = self.qual_var.get()
        playlist = self.playlist_var.get()
        if not url:
            mbox.showerror('Erro', 'Insira a URL do vídeo!')
            return
        if not os.path.isdir(output_path):
            mbox.showerror('Erro', 'Diretório de download inválido!')
            return
        self.download_btn.configure(state='disabled', text='Baixando...')
        self.progress.set(0)
        self.progress.pack(pady=10)
        self.status_label.configure(text='Iniciando download...')
        self.open_folder_btn.pack_forget()
        self.cancel_event.clear()
        self.cancel_btn.pack(pady=2)
        self.show_thumbnail(url)
        self.download_queue.append((url, fmt, output_path, qual, playlist))
        self.process_queue()

    def update_progress(self, percent, status=None):
        self.progress.set(percent)
        self.update_taskbar_progress(int(percent * 100))
        if status:
            self.status_label.configure(text=status)
        self.update_idletasks()

    def download(self, url, fmt, output_path, qual, playlist):
        try:
            def hook(d):
                if self.cancel_event.is_set():
                    raise Exception('Download cancelado pelo usuário.')
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    downloaded = d.get('downloaded_bytes', 0)
                    percent = min(downloaded / total, 1.0)
                    self.update_progress(percent, f"Baixando: {int(percent*100)}%")
                elif d['status'] == 'finished':
                    self.update_progress(1.0, 'Processando arquivo...')
            downloader.yt_dlp.utils.std_headers['User-Agent'] = downloader.yt_dlp.utils.random_user_agent()
            ydl_opts = {
                'progress_hooks': [hook],
                'format': 'bestaudio/best' if fmt == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'noplaylist': not playlist,
            }
            if fmt == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': qual,
                }]
            else:
                ydl_opts['merge_output_format'] = 'mp4'
            result = downloader.yt_dlp.YoutubeDL(ydl_opts)
            info = result.extract_info(url, download=True)
            if fmt == 'mp3':
                filename = os.path.splitext(result.prepare_filename(info))[0] + '.mp3'
            else:
                filename = result.prepare_filename(info)
            self.update_progress(1.0, 'Download concluído!')
            mbox.showinfo('Sucesso', f'Arquivo salvo: {filename}')
            notification.notify(title='YouTube Converter', message='Download finalizado com sucesso!', app_name='YouTube Converter')
            self.url_entry.delete(0, 'end')
            self.open_folder_btn.pack(pady=2)
            self.last_dir = output_path
            self.update_taskbar_progress(100)
            self.toast.show_toast('YouTube Converter', 'Download finalizado com sucesso!', duration=3, threaded=True)
        except Exception as e:
            self.update_progress(0)
            mbox.showerror('Erro', str(e))
        finally:
            self.download_btn.configure(state='normal', text='Baixar')
            self.status_label.configure(text='')
            self.progress.set(0)
            self.progress.pack_forget()
            self.cancel_btn.pack_forget()
            self.is_downloading = False
            self.update_taskbar_progress(0)
            self.process_queue()

    def process_queue(self):
        if not self.is_downloading and self.download_queue:
            self.is_downloading = True
            args = self.download_queue.pop(0)
            threading.Thread(target=self.download, args=args, daemon=True).start()

    def open_folder(self):
        try:
            os.startfile(self.dir_var.get())
        except Exception as e:
            mbox.showerror('Erro', f'Não foi possível abrir a pasta: {e}')

    def check_clipboard_for_url(self):
        try:
            url = self.clipboard_get()
            if url and re.match(r'https?://(www\.)?youtube\.com/watch\?v=|https?://youtu\.be/', url):
                if not self.url_entry.get():
                    self.url_entry.insert(0, url[:200])
                    self.show_thumbnail(url)
        except tk.TclError:
            pass
        self.after(1000, self.check_clipboard_for_url)

    def show_thumbnail(self, url):
        video_id = self.extract_video_id(url)
        if video_id:
            thumb_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
            try:
                resp = requests.get(thumb_url, timeout=5)
                img = Image.open(BytesIO(resp.content)).resize((180, 100))
                self.thumb_img = ImageTk.PhotoImage(img)
                self.thumb_label.configure(image=self.thumb_img, text='')
            except Exception:
                self.thumb_label.configure(text='[Miniatura indisponível]', image=None)
        else:
            self.thumb_label.configure(text='', image=None)

    def extract_video_id(self, url):
        match = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', url)
        return match.group(1) if match else None

    def cancel_download(self):
        self.cancel_event.set()
        self.status_label.configure(text='Cancelando...')

    def load_settings(self):
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_settings(self):
        self.settings['theme'] = self.theme_menu.get()
        self.settings['download_dir'] = self.dir_var.get()
        self.settings['quality'] = self.qual_var.get()
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)

    def set_custom_theme(self, theme_name):
        theme_info = self.theme_colors[theme_name]
        ctk.set_default_color_theme(theme_info['theme'])
        color = theme_info['color']
        entry_bg = theme_info.get('entry_bg', '#23272e')
        label_fg = theme_info.get('label_fg', '#8fa1b3')
        # Aplicar cor personalizada nos principais widgets
        self.download_btn.configure(fg_color=color, hover_color=color)
        self.progress.configure(progress_color=color)
        self.mp3_radio.configure(border_color=color, fg_color=color, hover_color=color)
        self.mp4_radio.configure(border_color=color, fg_color=color, hover_color=color)
        self.dir_btn.configure(fg_color=color, hover_color=color)
        self.open_folder_btn.configure(fg_color=color, hover_color=color)
        self.cancel_btn.configure(fg_color=color, hover_color=color)
        self.theme_btn.configure(fg_color=color, hover_color=color)
        # Ajuste para tema branco
        if theme_name == 'Branco':
            ctk.set_appearance_mode('light')
            self.main_frame.configure(fg_color='#f5f5f5')
            self.configure(bg='#e0e0e0')
            self.url_entry.configure(bg_color=entry_bg, fg_color=entry_bg, text_color='#222')
            self.dir_entry.configure(bg_color=entry_bg, fg_color=entry_bg, text_color='#222')
            self.status_label.configure(text_color=label_fg)
            self.url_label.configure(text_color='#222')
            self.dir_label.configure(text_color='#222')
            self.qual_label.configure(text_color='#222')
        else:
            ctk.set_appearance_mode('dark')
            self.main_frame.configure(fg_color='#23272e')
            self.configure(bg='#181c20')
            self.url_entry.configure(bg_color='#23272e', fg_color='#23272e', text_color='#fff')
            self.dir_entry.configure(bg_color='#23272e', fg_color='#23272e', text_color='#fff')
            self.status_label.configure(text_color=label_fg)
            self.url_label.configure(text_color='#8fa1b3')
            self.dir_label.configure(text_color='#8fa1b3')
            self.qual_label.configure(text_color='#8fa1b3')
        self.save_settings()

    def qual_menu_callback(self, value):
        self.save_settings()

    def __del__(self):
        self.save_settings()
