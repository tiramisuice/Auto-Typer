import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyautogui
import pyperclip
import time
import random
import threading
import re
from pynput import keyboard
from zhuyin_mapping import ZHUYIN_TO_CHINESE, COMMON_CHINESE_WORDS, is_chinese_character
import base64
from io import BytesIO

class AutoTyper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Typer Pro")
        
        # --- THEME & STYLING ---
        self.bg_color = '#2e3440'         # Nord dark
        self.fg_color = '#d8dee9'         # Nord light gray
        self.frame_color = '#3b4252'      # Nord slightly lighter dark
        self.accent_color = '#88c0d0'     # Nord blue
        self.success_color = '#a3be8c'    # Nord green
        self.error_color = '#bf616a'      # Nord red
        self.warning_color = '#ebcb8b'    # Nord yellow

        self.root.configure(bg=self.bg_color)
        
        # Set a modern theme
        style = ttk.Style(self.root)
        style.theme_use('clam')
        
        # Configure custom styles
        self.configure_styles(style)

        # Set App Icon
        self.set_app_icon()
        
        # Variables
        self.is_typing = False
        self.typing_thread = None
        self.stop_typing = False
        
        # Hotkey settings
        self.start_hotkey = 'ctrl+shift+s'
        self.stop_hotkey = 'ctrl+shift+x'
        
        # Typing settings
        self.min_delay = 0.05
        self.max_delay = 0.15
        self.word_delay = 0.3
        self.sentence_delay = 0.8
        
        # Human-like typing features
        self.enable_errors = True
        self.error_rate = 0.15
        self.correction_rate = 0.8
        self.thinking_pause_rate = 0.1
        self.speed_variation = True
        
        # Error dictionaries for simulation
        self.setup_error_data()
        
        # Setup UI and other components
        self.setup_ui()
        self.setup_hotkeys()
        
        # Set a default and minimum size for the window
        self.root.geometry("820x720")
        self.root.minsize(780, 680)

    def configure_styles(self, style):
        """Configure custom ttk styles for a modern look."""
        # General widget styles
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI', 10))
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabelframe', background=self.bg_color, bordercolor=self.accent_color)
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.accent_color, font=('Segoe UI', 11, 'bold'))
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color, font=('Segoe UI', 10))
        style.map('TCheckbutton',
                  background=[('active', self.frame_color)],
                  indicatorcolor=[('selected', self.accent_color)])
        
        # Button styles
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10, borderwidth=0)
        style.map('TButton',
                  background=[('!active', self.frame_color), ('active', self.accent_color)],
                  foreground=[('!active', self.fg_color)])

        # Special buttons
        style.configure('Success.TButton', background=self.success_color, foreground='#2e3440')
        style.map('Success.TButton', background=[('active', '#8fbcbb')])
        style.configure('Error.TButton', background=self.error_color, foreground='#2e3440')
        style.map('Error.TButton', background=[('active', '#d08770')])
        
        # Combobox style
        self.root.option_add('*TCombobox*Listbox*Background', self.frame_color)
        self.root.option_add('*TCombobox*Listbox*Foreground', self.fg_color)
        self.root.option_add('*TCombobox*Listbox*selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox*selectForeground', self.bg_color)
        style.configure('TCombobox', 
                        fieldbackground=self.frame_color, 
                        background=self.frame_color,
                        arrowcolor=self.fg_color,
                        foreground=self.fg_color,
                        bordercolor=self.frame_color,
                        lightcolor=self.frame_color,
                        darkcolor=self.frame_color)
        style.map('TCombobox', fieldbackground=[('readonly', self.frame_color)])

    def set_app_icon(self):
        """Sets the application icon by loading icon.png from the local directory."""
        try:
            # Keep a reference to the image to prevent it from being garbage collected
            self.icon_image = tk.PhotoImage(file='icon.png')
            self.root.iconphoto(True, self.icon_image)
        except tk.TclError:
            print("Could not load icon. Please ensure 'icon.png' is in the script's directory.")
        except Exception as e:
            print(f"An unexpected error occurred while loading icon: {e}")

    def setup_error_data(self):
        """Setup error simulation data"""
        # Characters that need copy-pasting for reliability
        self.paste_chars = "，。！？；：（）「」『』、"
        
        # Common homophone errors (同音字錯誤)
        self.homophone_errors = {
            "你": ["妳"],
            "的": ["得", "地"],
            "在": ["再"],
            "做": ["作"],
            "他": ["她"],
            "那": ["哪"],
            "這": ["者"],
            "時": ["是", "事"],
            "事": ["是", "時"],
            "已": ["以"],
            "以": ["已"],
            "會": ["回"],
            "回": ["會"],
            "年": ["念"],
            "念": ["年"],
            "聽": ["廳"],
            "廳": ["聽"],
            "話": ["畫"],
            "畫": ["話"],
            "帶": ["代"],
            "代": ["帶"],
            "錢": ["前"],
            "前": ["錢"],
            "先": ["仙"],
            "仙": ["先"],
            "現": ["線"],
            "線": ["現"],
            "經": ["精"],
            "精": ["經"]
        }
        
        # Similar looking characters (形似字錯誤)
        self.similar_char_errors = {
            "己": ["已"],
            "已": ["己"],
            "未": ["末"],
            "末": ["未"],
            "干": ["千"],
            "千": ["干"],
            "土": ["士"],
            "士": ["土"],
            "戶": ["尸"],
            "尸": ["戶"],
            "貝": ["見"],
            "見": ["貝"],
            "刀": ["力"],
            "力": ["刀"],
            "入": ["人"],
            "人": ["入"],
            "木": ["本"],
            "本": ["木"],
            "大": ["太"],
            "太": ["大"]
        }
        
        # English punctuation to Chinese punctuation errors
        self.punctuation_errors = {
            ",": "，",
            ".": "。",
            "!": "！",
            "?": "？",
            ";": "；",
            ":": "：",
            "(": "（",
            ")": "）"
        }
        
        # Common English typing errors
        self.english_errors = {
            "the": ["teh", "hte"],
            "and": ["adn", "nad"],
            "you": ["yuo", "oyu"],
            "that": ["taht", "htat"],
            "have": ["ahve", "hvae"],
            "with": ["wtih", "whit"],
            "this": ["tihs", "htis"],
            "they": ["tehy", "htey"],
            "from": ["form", "fomr"],
            "been": ["bene", "been"],
            "said": ["siad", "said"],
            "each": ["eahc", "caeh"],
            "which": ["whihc", "hwich"],
            "their": ["thier", "theyr"],
            "time": ["tiem", "tmie"],
            "will": ["wil", "wlil"],
            "about": ["aobut", "baout"],
            "would": ["woudl", "owuld"],
            "there": ["tehre", "theer"],
            "could": ["coudl", "ocudl"]
        }
        
    def setup_ui(self):
        # --- Main Layout Configuration ---
        # Use a grid on the root to center the main content column.
        # The outer rows (0, 2) and columns (0, 2) are 'spacers' that expand.
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0) # Content row, no extra vertical space
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0) # Content column
        self.root.grid_columnconfigure(2, weight=1)

        # This is the main container for all widgets, placed in the center of the root grid.
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        # Configure the content_frame's grid. The text area's row (2) will be the one to expand.
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(2, weight=1) # Make the text_frame row responsive

        # --- Widget Creation ---
        
        # Title
        title_label = ttk.Label(content_frame, text="Auto Typer for Traditional Chinese & English", 
                              font=("Segoe UI", 18, "bold"), anchor='center')
        title_label.grid(row=0, column=0, pady=(10, 10), sticky="ew")
        
        # Instructions
        instructions = ttk.Label(content_frame, 
                              text="Type or paste your text below. Mix English and Traditional Chinese freely.\nHotkeys: Ctrl+Shift+S (Start), Ctrl+Shift+X (Stop)", 
                              font=("Segoe UI", 10), anchor='center', justify=tk.CENTER)
        instructions.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Text input area (this is the parent frame that will expand)
        text_frame = ttk.Frame(content_frame)
        text_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(text_frame, text="Text to Type:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(text_frame, height=8, font=("Segoe UI", 11),
                                             bg=self.frame_color, fg=self.fg_color, insertbackground=self.fg_color,
                                             relief='flat', borderwidth=2, padx=5, pady=5)
        self.text_area.grid(row=1, column=0, sticky="nsew")
        
        # Sample text button
        sample_btn = ttk.Button(text_frame, text="Load Sample Text", command=self.load_sample_text)
        sample_btn.grid(row=2, column=0, pady=10)
        
        # --- Settings frame ---
        self.settings_frame = ttk.LabelFrame(content_frame, text="Settings", style='TLabelframe')
        self.settings_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        # --- Speed Settings ---
        speed_frame = ttk.Frame(self.settings_frame)
        speed_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(speed_frame, text="Typing Speed:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.speed_var = tk.StringVar(value="Medium")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["Very Slow", "Slow", "Medium", "Fast", "Very Fast"], 
                                  state="readonly", width=15)
        speed_combo.pack(side=tk.LEFT, padx=5)
        speed_combo.bind("<<ComboboxSelected>>", self.update_speed)
        
        # Word by word option
        self.word_by_word = tk.BooleanVar(value=True)
        word_check = ttk.Checkbutton(speed_frame, text="Type word by word", 
                                   variable=self.word_by_word, style='TCheckbutton')
        word_check.pack(side=tk.LEFT, padx=(20, 5))
        
        # --- Chinese Input Method ---
        input_frame = ttk.Frame(self.settings_frame)
        input_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(input_frame, text="Chinese Input:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_method_var = tk.StringVar(value="Direct")
        input_combo = ttk.Combobox(input_frame, textvariable=self.input_method_var, 
                                 values=["Direct", "Zhuyin", "Copy-Paste"], 
                                 state="readonly", width=15)
        input_combo.pack(side=tk.LEFT, padx=5)
        
        help_btn = ttk.Button(input_frame, text="❓ Setup", command=self.show_input_help, width=10)
        help_btn.pack(side=tk.LEFT, padx=5)
        
        test_btn = ttk.Button(input_frame, text="🔬 Test", command=self.test_mappings, width=10)
        test_btn.pack(side=tk.LEFT, padx=5)

        # --- Human-like Features ---
        human_frame = ttk.Frame(self.settings_frame)
        human_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(human_frame, text="Human-like Features", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Error simulation settings
        error_frame = ttk.Frame(human_frame)
        error_frame.pack(fill=tk.X, pady=4, anchor='w')
        
        self.enable_errors_var = tk.BooleanVar(value=True)
        error_check = ttk.Checkbutton(error_frame, text="Enable typing errors", 
                                   variable=self.enable_errors_var)
        error_check.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(error_frame, text="Rate:").pack(side=tk.LEFT, padx=(5, 5))
        self.error_rate_var = tk.StringVar(value="15")
        error_rate_spin = ttk.Spinbox(error_frame, from_=0, to=50, width=5, 
                                   textvariable=self.error_rate_var)
        error_rate_spin.pack(side=tk.LEFT)
        ttk.Label(error_frame, text="%").pack(side=tk.LEFT)
        
        # Speed variation settings
        speed_var_frame = ttk.Frame(human_frame)
        speed_var_frame.pack(fill=tk.X, pady=4, anchor='w')
        
        self.speed_variation_var = tk.BooleanVar(value=True)
        speed_var_check = ttk.Checkbutton(speed_var_frame, text="Variable typing speed", 
                                       variable=self.speed_variation_var)
        speed_var_check.pack(side=tk.LEFT)
        
        # Thinking pauses settings
        pause_frame = ttk.Frame(human_frame)
        pause_frame.pack(fill=tk.X, pady=4, anchor='w')

        self.thinking_pauses_var = tk.BooleanVar(value=True)
        thinking_check = ttk.Checkbutton(pause_frame, text="Thinking pauses",
                                       variable=self.thinking_pauses_var)
        thinking_check.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(pause_frame, text="Freq:").pack(side=tk.LEFT)
        self.pause_freq_var = tk.StringVar(value="10")
        pause_freq_spin = ttk.Spinbox(pause_frame, from_=0, to=100, width=4,
                                     textvariable=self.pause_freq_var)
        pause_freq_spin.pack(side=tk.LEFT)
        ttk.Label(pause_frame, text="%").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(pause_frame, text="Duration:").pack(side=tk.LEFT)
        self.min_pause_var = tk.StringVar(value="0.5")
        min_pause_spin = ttk.Spinbox(pause_frame, from_=0.1, to=10, increment=0.1, width=5,
                                    textvariable=self.min_pause_var)
        min_pause_spin.pack(side=tk.LEFT)
        ttk.Label(pause_frame, text="s to").pack(side=tk.LEFT, padx=(5, 5))
        self.max_pause_var = tk.StringVar(value="2.0")
        max_pause_spin = ttk.Spinbox(pause_frame, from_=0.1, to=10, increment=0.1, width=5,
                                    textvariable=self.max_pause_var)
        max_pause_spin.pack(side=tk.LEFT)
        ttk.Label(pause_frame, text="s").pack(side=tk.LEFT)
        
        # Auto correction settings
        correction_frame = ttk.Frame(human_frame)
        correction_frame.pack(fill=tk.X, pady=4, anchor='w')
        
        self.auto_correct_var = tk.BooleanVar(value=True)
        correct_check = ttk.Checkbutton(correction_frame, text="Auto-correct errors", 
                                     variable=self.auto_correct_var)
        correct_check.pack(side=tk.LEFT, padx=(0, 22))
        
        ttk.Label(correction_frame, text="Rate:").pack(side=tk.LEFT, padx=(5, 5))
        self.correction_rate_var = tk.StringVar(value="80")
        correction_rate_spin = ttk.Spinbox(correction_frame, from_=0, to=100, width=5, 
                                        textvariable=self.correction_rate_var)
        correction_rate_spin.pack(side=tk.LEFT)
        ttk.Label(correction_frame, text="%").pack(side=tk.LEFT)
        
        # --- Main Control Buttons ---
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=4, column=0, pady=20)
        
        self.start_btn = ttk.Button(button_frame, text="▶ Start Typing", 
                                  command=self.start_typing, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=10, ipady=10, ipadx=10)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop Typing", 
                                 command=self.stop_typing_action, style='Error.TButton', state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=10, ipady=10, ipadx=10)
        
        # Status label
        self.status_label = ttk.Label(content_frame, text="Ready to type", 
                                    font=("Segoe UI", 10, "italic"), anchor='center')
        self.status_label.grid(row=5, column=0, pady=10, sticky="ew")

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        def on_start_hotkey():
            if not self.is_typing:
                self.start_typing()
                
        def on_stop_hotkey():
            if self.is_typing:
                self.stop_typing_action()
        
        # Setup keyboard listener for hotkeys
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+s': on_start_hotkey,
            '<ctrl>+<shift>+x': on_stop_hotkey
        })
        self.hotkey_listener.start()
        
    def update_speed(self, event=None):
        """Update typing speed based on selection"""
        speed = self.speed_var.get()
        speed_settings = {
            "Very Slow": (0.1, 0.3, 0.5, 1.2),
            "Slow": (0.08, 0.2, 0.4, 1.0),
            "Medium": (0.05, 0.15, 0.3, 0.8),
            "Fast": (0.03, 0.1, 0.2, 0.5),
            "Very Fast": (0.01, 0.05, 0.1, 0.3)
        }
        
        if speed in speed_settings:
            self.min_delay, self.max_delay, self.word_delay, self.sentence_delay = speed_settings[speed]
            
    def load_sample_text(self):
        """Load sample text mixing English and Traditional Chinese with error-prone content"""
        sample = """Hello, 你好! 我是一個學生。你是我的朋友嗎?

Today I want to write about 我的家庭. My family consists of 爸爸, 媽媽, and 我.

我們住在一個小城市. The weather here is very 好. 我喜歡在這裡學習和工作.

In my free time, I like to 看書 and 聽音樂. Sometimes I also 寫作業 or 和朋友聊天.

I have been studying Chinese for years. It's difficult but I think I will succeed.

你現在在做什麼? 我已經完成了作業, 現在準備去睡覺了。

This is a good practice for typing both English and Traditional Chinese characters naturally. The punctuation mixing can be tricky too!"""
        
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert('1.0', sample)
        
    def show_input_help(self):
        """Show input method setup help"""
        help_text = """Input Method Setup Help:

🔧 **DIRECT (Recommended)**
   - Types Chinese characters directly.
   - Works with most input methods and is the most reliable.

🔧 **ZHUYIN (Advanced)**
   - Simulates traditional Zhuyin (注音) input.
   - Requires Microsoft Bopomofo IME to be enabled and active.
   - More "human-like" but needs proper setup.

🔧 **COPY-PASTE (Fallback)**
   - Uses the clipboard to paste characters.
   - A backup method if others fail. Slowest but most compatible.

---
**ZHUYIN SETUP GUIDE**
1. Enable **Microsoft Bopomofo** IME in Windows settings.
2. Switch to Chinese input mode (**Win + Space**).
3. Ensure the cursor is in the target application before starting.
4. Use the "**🔬 Test**" button to verify mappings.
---

**TROUBLESHOOTING**
- **Google Docs**: If 'Direct' fails, use 'Copy-Paste'.
- **Windows Setup**: 
  1. Go to `Settings > Time & Language > Language`.
  2. Add "**Chinese (Traditional, Taiwan)**".
  3. Under its options, install the "**Microsoft Bopomofo**" input method.
"""
        
        # Create a modern-looking message box
        top = tk.Toplevel(self.root)
        top.title("Setup Help")
        top.geometry("450x400")
        top.configure(bg=self.bg_color)
        
        msg_frame = ttk.Frame(top, padding=20)
        msg_frame.pack(expand=True, fill=tk.BOTH)
        
        lbl = ttk.Label(msg_frame, text=help_text, justify=tk.LEFT, wraplength=400)
        lbl.pack(pady=10)
        
        ok_btn = ttk.Button(msg_frame, text="OK", command=top.destroy, style="Success.TButton")
        ok_btn.pack(pady=10)
        
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)
        
    def get_typing_delay(self, char_type='normal'):
        """Get random delay to simulate human typing with variation"""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        if self.speed_variation_var.get():
            # Different speeds for different character types
            if char_type == 'chinese':
                # Chinese characters typically take longer
                base_delay *= random.uniform(1.5, 2.5)
            elif char_type == 'english':
                # English characters are faster
                base_delay *= random.uniform(0.8, 1.2)
            elif char_type == 'punctuation':
                # Punctuation has moderate speed
                base_delay *= random.uniform(1.0, 1.5)
            
            # Add random variation to simulate human inconsistency
            variation = random.uniform(0.5, 2.0)
            base_delay *= variation
            
            # Occasionally add longer pauses (fatigue, distraction)
            if random.random() < 0.05:  # 5% chance
                base_delay += random.uniform(0.3, 1.0)
        
        return max(0.01, base_delay)  # Ensure minimum delay
    
    def should_make_error(self):
        """Determine if an error should be made"""
        if not self.enable_errors_var.get():
            return False
        error_rate = float(self.error_rate_var.get()) / 100.0
        return random.random() < error_rate
    
    def should_correct_error(self):
        """Determine if an error should be corrected"""
        if not self.auto_correct_var.get():
            return False
        correction_rate = float(self.correction_rate_var.get()) / 100.0
        return random.random() < correction_rate
    
    def should_pause_for_thinking(self):
        """Determine if should pause for thinking based on UI settings"""
        if not self.thinking_pauses_var.get():
            return False
        try:
            pause_rate = float(self.pause_freq_var.get()) / 100.0
            return random.random() < pause_rate
        except ValueError:
            return False  # Default to no pause if value is invalid
    
    def get_thinking_pause(self):
        """Get thinking pause duration from UI settings"""
        try:
            min_d = float(self.min_pause_var.get())
            max_d = float(self.max_pause_var.get())
            # Ensure min is not greater than max
            if min_d > max_d:
                min_d = max_d
            return random.uniform(min_d, max_d)
        except ValueError:
            return random.uniform(0.5, 2.0)  # Return default on invalid value
    
    def simulate_error(self, char):
        """Simulate a typing error for the given character"""
        if is_chinese_character(char):
            # Try homophone error first
            if char in self.homophone_errors:
                return random.choice(self.homophone_errors[char])
            # Try similar character error
            elif char in self.similar_char_errors:
                return random.choice(self.similar_char_errors[char])
            # Random character replacement (rare)
            elif random.random() < 0.3:
                similar_chars = list(self.homophone_errors.keys()) + list(self.similar_char_errors.keys())
                return random.choice(similar_chars)
        else:
            # English character errors
            if char.lower() in 'aeiou':  # Vowel confusion
                vowels = 'aeiou'
                return random.choice([v for v in vowels if v != char.lower()])
            elif char.lower() in 'qwertyuiop':  # Adjacent key errors
                adjacent = {'q': 'wa', 'w': 'qes', 'e': 'wrd', 'r': 'etf', 't': 'ryg',
                           'y': 'tuh', 'u': 'yij', 'i': 'uok', 'o': 'ipl', 'p': 'ol'}
                if char.lower() in adjacent:
                    return random.choice(adjacent[char.lower()])
            # Random adjacent character
            keyboard_layout = 'qwertyuiopasdfghjklzxcvbnm'
            idx = keyboard_layout.find(char.lower())
            if idx >= 0:
                # Pick adjacent character
                choices = []
                if idx > 0: choices.append(keyboard_layout[idx-1])
                if idx < len(keyboard_layout)-1: choices.append(keyboard_layout[idx+1])
                if choices:
                    return random.choice(choices)
        
        return char  # Return original if no error pattern found
    
    def type_with_corrections(self, text_to_type):
        """Type text with error correction simulation"""
        errors_made = []  # Track errors for correction
        
        for char in text_to_type:
            if self.stop_typing:
                break
                
            # Thinking pause before difficult characters
            if self.should_pause_for_thinking() and (is_chinese_character(char) or char in self.paste_chars):
                time.sleep(self.get_thinking_pause())
                
            # Determine if error should be made
            if self.should_make_error():
                error_char = self.simulate_error(char)
                if error_char != char:
                    # Type the wrong character first
                    if is_chinese_character(error_char) or error_char in self.paste_chars:
                        pyperclip.copy(error_char)
                        pyautogui.hotkey('ctrl', 'v')
                    else:
                        pyautogui.write(error_char)
                    
                    char_type = 'chinese' if is_chinese_character(error_char) or error_char in self.paste_chars else 'english'
                    time.sleep(self.get_typing_delay(char_type))
                    
                    # Store error for potential correction
                    errors_made.append((error_char, char))
                    
                    # Decide whether to correct immediately or later
                    if self.should_correct_error():
                        correction_delay = random.uniform(0.2, 1.5)
                        time.sleep(correction_delay)
                        
                        # Backspace to remove error
                        pyautogui.press('backspace')
                        time.sleep(0.1)
                        
                        # Type correct character
                        if is_chinese_character(char) or char in self.paste_chars:
                            pyperclip.copy(char)
                            pyautogui.hotkey('ctrl', 'v')
                        else:
                            pyautogui.write(char)
                        
                        char_type = 'chinese' if is_chinese_character(char) or char in self.paste_chars else 'english'
                        time.sleep(self.get_typing_delay(char_type))
                        
                        # Remove from errors list
                        errors_made = [e for e in errors_made if e[1] != char]
                    continue
            
            # --- Type correct character (no error made) ---
            
            # Handle CJK characters and punctuation that need pasting
            if is_chinese_character(char) or char in self.paste_chars:
                pyperclip.copy(char)
                pyautogui.hotkey('ctrl', 'v')
                char_type = 'chinese'
            
            # Handle English characters and punctuation
            else:
                # Simulate English punctuation being corrected to Chinese punctuation
                if char in self.punctuation_errors and random.random() < 0.3:
                    chinese_punc = self.punctuation_errors[char]
                    # Simulate typing English punc, backspace, then Chinese punc
                    if random.random() < 0.5:
                        pyautogui.write(char)  # Type English punc like '.'
                        time.sleep(0.2)
                        pyautogui.press('backspace')
                        time.sleep(0.1)
                        pyperclip.copy(chinese_punc)  # Paste Chinese punc like '。'
                        pyautogui.hotkey('ctrl', 'v')
                    else: # Or just "correctly" type the Chinese punc
                        pyperclip.copy(chinese_punc)
                        pyautogui.hotkey('ctrl', 'v')
                    
                    char_type = 'punctuation'
                else:
                    # Type normal English characters and punctuation
                    pyautogui.write(char)
                    char_type = 'punctuation' if char in '.,!?;:()' else 'english'
            
            time.sleep(self.get_typing_delay(char_type))
    
    def find_zhuyin_for_character(self, char):
        """Find Zhuyin pronunciation for a given character"""
        for zhuyin, chinese_char in ZHUYIN_TO_CHINESE.items():
            if char == chinese_char:
                return zhuyin
        return None
        
    def simulate_zhuyin_input(self, chinese_char):
        """Simulate Chinese character input based on selected method"""
        input_method = self.input_method_var.get()
        
        if input_method == "Direct":
            # Try direct character input
            try:
                pyautogui.write(chinese_char)
                time.sleep(self.get_typing_delay('chinese'))
                return True
            except:
                # Fallback to copy-paste
                pyperclip.copy(chinese_char)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(self.get_typing_delay('chinese'))
                return True
                
        elif input_method == "Copy-Paste":
            # Use copy-paste method with human-like features
            try:
                pyperclip.copy(chinese_char)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(self.get_typing_delay('chinese'))
                return True
            except:
                return False
                
        elif input_method == "Zhuyin":
            # Improved Zhuyin input method
            zhuyin = self.find_zhuyin_for_character(chinese_char)
            
            if zhuyin:
                try:
                    # Debug output
                    print(f"Typing '{chinese_char}' using Zhuyin: {zhuyin}")
                    
                    # Convert Zhuyin to keyboard keys
                    keys = self.convert_zhuyin_to_keys(zhuyin)
                    print(f"Keyboard keys: {keys}")
                    
                    if not keys:
                        # Fallback to copy-paste if no key mapping
                        pyperclip.copy(chinese_char)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(self.get_typing_delay())
                        return True
                    
                    # Type each key with proper timing
                    for key in keys:
                        if self.stop_typing:
                            return False
                        pyautogui.press(key)
                        time.sleep(0.05)  # Small delay between keys
                    
                    # Wait for candidate window to appear
                    time.sleep(0.3)
                    
                    # Press space to select first candidate
                    pyautogui.press('space')
                    time.sleep(self.get_typing_delay('chinese'))
                    
                    return True
                    
                except Exception as e:
                    print(f"Zhuyin error for '{chinese_char}': {e}")
                    # Fallback to copy-paste
                    try:
                        pyperclip.copy(chinese_char)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(self.get_typing_delay('chinese'))
                        return True
                    except:
                        return False
            else:
                # No Zhuyin mapping found, use copy-paste
                print(f"No Zhuyin mapping found for '{chinese_char}', using copy-paste")
                try:
                    pyperclip.copy(chinese_char)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(self.get_typing_delay('chinese'))
                    return True
                except:
                    return False
        
        return True
    
    def convert_zhuyin_to_keys(self, zhuyin):
        """Convert Zhuyin symbols to keyboard keys for Microsoft Bopomofo (IMPROVED)"""
        # Updated and more comprehensive Microsoft Bopomofo keyboard mapping
        zhuyin_to_key = {
            # Initials - Row 1 (numbers)
            'ㄅ': '1', 'ㄉ': '2', 'ㄓ': '3', 'ㄏ': '4', 'ㄐ': '5',
            'ㄔ': '6', 'ㄗ': '7', 'ㄘ': '8', 'ㄙ': '9', 'ㄖ': '0',
            
            # Initials - Row 2 (QWERTY)
            'ㄆ': 'q', 'ㄊ': 'w', 'ㄍ': 'e', 'ㄎ': 'r', 'ㄑ': 't',
            'ㄕ': 'y', 'ㄞ': 'u', 'ㄟ': 'i', 'ㄠ': 'o', 'ㄡ': 'p',
            
            # Initials - Row 3 (ASDF)
            'ㄇ': 'a', 'ㄋ': 's', 'ㄌ': 'd', 'ㄒ': 'f', 'ㄢ': 'g',
            'ㄣ': 'h', 'ㄤ': 'j', 'ㄥ': 'k', 'ㄦ': 'l', 'ㄧ': ';',
            
            # Finals - Row 4 (ZXCV)
            'ㄈ': 'z', 'ㄨ': 'x', 'ㄩ': 'c', 'ㄚ': 'v', 'ㄛ': 'b',
            'ㄜ': 'n', 'ㄝ': 'm', 'ㄤ': 'j', 'ㄥ': 'k',
            
            # Tone marks - typically on number row with different combinations
            # 'ˊ': '/', '˙': ',', 'ˇ': '-', 'ˋ': '.', # Removed direct tone key mappings
            # '': ''  # No tone (first tone) -> This entry is not needed if tones are handled by IME
        }
        
        keys = []
        tone_symbols = ['ˊ', 'ˇ', 'ˋ', '˙'] # Define tone symbols to ignore for direct key press
        for char_zhuyin in zhuyin: # Renamed char to char_zhuyin for clarity
            if char_zhuyin in tone_symbols:
                continue # Skip direct key press for tone symbols
            if char_zhuyin in zhuyin_to_key:
                key = zhuyin_to_key[char_zhuyin]
                if key:  # Only add non-empty keys
                    keys.append(key)
            else:
                # Allow empty string for cases like first tone where no symbol is present
                if char_zhuyin != '':
                    print(f"Warning: No key mapping for Zhuyin character '{char_zhuyin}'")
        
        return keys
        
    def type_text_word_by_word(self, text):
        """Type text word by word with human-like features"""
        # Split text into words, preserving spaces and punctuation
        words = re.findall(r'\S+|\s+', text)
        
        for word in words:
            if self.stop_typing:
                break
                
            word = word.strip()
            if not word:
                pyautogui.write(' ')
                time.sleep(self.word_delay)
                continue
            
            # Check for whole word errors (English words)
            if not any(is_chinese_character(c) for c in word):
                # This is an English word, check for common word errors
                word_lower = word.lower()
                if word_lower in self.english_errors and self.should_make_error():
                    error_word = random.choice(self.english_errors[word_lower])
                    
                    # Type the wrong word
                    pyautogui.write(error_word)
                    time.sleep(self.get_typing_delay('english') * len(error_word))
                    
                    # Correct if should correct
                    if self.should_correct_error():
                        correction_delay = random.uniform(0.5, 2.0)
                        time.sleep(correction_delay)
                        
                        # Select and delete wrong word
                        for _ in range(len(error_word)):
                            pyautogui.press('backspace')
                            time.sleep(0.05)
                        
                        # Type correct word
                        self.type_with_corrections(word)
                    
                    # Add space after word (except for punctuation)
                    if word and not word[-1] in '.,!?;:，。！？；：':
                        pyautogui.write(' ')
                    
                    # Pause between words
                    time.sleep(self.word_delay)
                    continue
            
            # Type word character by character with human-like features
            self.type_with_corrections(word)
                    
            # Add space after word (except for punctuation)
            if word and not word[-1] in '.,!?;:，。！？；：':
                pyautogui.write(' ')
                
            # Pause between words with variation
            word_pause = self.word_delay
            if self.speed_variation_var.get():
                word_pause *= random.uniform(0.5, 1.5)
            time.sleep(word_pause)
            
            # Longer pause after sentences
            if word and word[-1] in '.!?。！？':
                sentence_pause = self.sentence_delay
                if self.speed_variation_var.get():
                    sentence_pause *= random.uniform(0.8, 2.0)
                time.sleep(sentence_pause)
                
    def type_text_character_by_character(self, text):
        """Type text character by character with human-like features"""
        for char in text:
            if self.stop_typing:
                break
                
            if char == '\n':
                pyautogui.press('enter')
                pause = self.sentence_delay
                if self.speed_variation_var.get():
                    pause *= random.uniform(0.5, 1.5)
                time.sleep(pause)
            elif char == ' ':
                pyautogui.write(' ')
                pause = self.word_delay
                if self.speed_variation_var.get():
                    pause *= random.uniform(0.3, 1.2)
                time.sleep(pause)
            else:
                # Use human-like typing for each character
                self.type_with_corrections(char)
                
            # Longer pause after sentences
            if char in '.!?。！？':
                sentence_pause = self.sentence_delay
                if self.speed_variation_var.get():
                    sentence_pause *= random.uniform(0.8, 2.0)
                time.sleep(sentence_pause)
                
    def typing_worker(self):
        """Worker thread for typing"""
        try:
            # Get text from text area, correctly handling the final newline
            text = self.text_area.get('1.0', tk.END).rstrip('\n').strip()
            if not text:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "Please enter some text to type."))
                return
                
            # Give user time to switch to target application
            for i in range(3, 0, -1):
                if self.stop_typing:
                    return
                self.root.after(0, lambda i=i: self.status_label.config(text=f"Starting in {i}..."))
                time.sleep(1)
                
            self.root.after(0, lambda: self.status_label.config(text="Typing in progress..."))
            
            # Type the text
            if self.word_by_word.get():
                self.type_text_word_by_word(text)
            else:
                self.type_text_character_by_character(text)
                
            if not self.stop_typing:
                self.root.after(0, lambda: self.status_label.config(text="Typing completed!"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Typing stopped by user."))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.is_typing = False
            self.stop_typing = False
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
            
    def start_typing(self):
        """Start the typing process"""
        if self.is_typing:
            return
            
        self.is_typing = True
        self.stop_typing = False
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Start typing in a separate thread
        self.typing_thread = threading.Thread(target=self.typing_worker, daemon=True)
        self.typing_thread.start()
        
    def stop_typing_action(self):
        """Stop the typing process"""
        if self.is_typing:
            self.stop_typing = True
            self.status_label.config(text="Stopping...")
            self.stop_btn.config(state='disabled')
            
    def on_closing(self):
        """Handle application closing"""
        self.stop_typing = True
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def test_mappings(self):
        """Test what Zhuyin mappings are available for current text"""
        text = self.text_area.get('1.0', tk.END).strip()
        if not text:
            messagebox.showinfo("Test Results", "Please enter some text first.")
            return
            
        results = []
        total_chinese = 0
        mapped_chinese = 0
        
        for char in text:
            if is_chinese_character(char):
                total_chinese += 1
                zhuyin = self.find_zhuyin_for_character(char)
                if zhuyin:
                    mapped_chinese += 1
                    keys = self.convert_zhuyin_to_keys(zhuyin)
                    results.append(f"'{char}' → {zhuyin} → keys: {keys}")
                else:
                    results.append(f"'{char}' → NO MAPPING (will use copy-paste)")
                    
        if results:
            coverage = f"Coverage: {mapped_chinese}/{total_chinese} characters have Zhuyin mappings\n\n"
            result_text = "Zhuyin Mappings Test:\n\n" + coverage + "\n".join(results)
        else:
            result_text = "No Chinese characters found in text."
            
        # Show results in a scrollable dialog
        result_window = tk.Toplevel(self.root)
        result_window.title("Mapping Test Results")
        result_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', result_text)
        text_widget.config(state='disabled', bg=self.frame_color, fg=self.fg_color, font=("Consolas", 10))

if __name__ == "__main__":
    # Disable pyautogui failsafe for better UX (optional)
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
    
    app = AutoTyper()
    app.run() 