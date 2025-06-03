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

class AutoTyper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Typer - Traditional Chinese & English")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_typing = False
        self.typing_thread = None
        self.stop_typing = False
        self.settings_collapsed = False
        
        # Hotkey settings
        self.start_hotkey = 'ctrl+shift+s'
        self.stop_hotkey = 'ctrl+shift+x'
        
        # Typing settings
        self.min_delay = 0.05  # Minimum delay between characters (50ms)
        self.max_delay = 0.15  # Maximum delay between characters (150ms)
        self.word_delay = 0.3  # Delay between words
        self.sentence_delay = 0.8  # Delay between sentences
        
        self.setup_ui()
        self.setup_hotkeys()
        self.check_window_size()
        
    def check_window_size(self):
        """Check window size and adjust layout accordingly"""
        def check_size():
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Consider small screen if width < 700 or height < 500
            is_small_screen = width < 700 or height < 500
            
            if is_small_screen and not self.settings_collapsed:
                self.collapse_settings()
            elif not is_small_screen and self.settings_collapsed:
                self.expand_settings()
                
        # Check size periodically
        self.root.after(500, lambda: [check_size(), self.check_window_size()])
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Auto Typer for Traditional Chinese & English", 
                              font=("Arial", 16, "bold"), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                              text="Type or paste your text below. Mix English and Traditional Chinese freely.\nHotkeys: Ctrl+Shift+S (Start), Ctrl+Shift+X (Stop)", 
                              font=("Arial", 10), bg='#f0f0f0', fg='#666')
        instructions.pack(pady=5)
        
        # Text input area
        text_frame = tk.Frame(self.root, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(text_frame, text="Text to Type:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(anchor='w')
        
        self.text_area = scrolledtext.ScrolledText(text_frame, height=15, font=("Arial", 11))
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Sample text button
        sample_btn = tk.Button(text_frame, text="Load Sample Text", command=self.load_sample_text,
                              bg='#e0e0e0', relief='raised')
        sample_btn.pack(pady=5)
        
        # Settings frame with collapse/expand functionality
        settings_header_frame = tk.Frame(self.root, bg='#f0f0f0')
        settings_header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.settings_toggle_btn = tk.Button(settings_header_frame, text="▼ Typing Settings", 
                                           command=self.toggle_settings, bg='#d0d0d0', 
                                           font=("Arial", 10, "bold"), relief='flat')
        self.settings_toggle_btn.pack(side=tk.LEFT)
        
        self.settings_frame = tk.LabelFrame(self.root, text="", 
                                          bg='#f0f0f0', padx=10, pady=10)
        self.settings_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Speed settings
        speed_frame = tk.Frame(self.settings_frame, bg='#f0f0f0')
        speed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(speed_frame, text="Typing Speed:", bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.speed_var = tk.StringVar(value="Medium")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["Very Slow", "Slow", "Medium", "Fast", "Very Fast"], 
                                  state="readonly", width=15)
        speed_combo.pack(side=tk.LEFT, padx=10)
        speed_combo.bind("<<ComboboxSelected>>", self.update_speed)
        
        # Word by word option
        self.word_by_word = tk.BooleanVar(value=True)
        word_check = tk.Checkbutton(speed_frame, text="Type word by word", 
                                   variable=self.word_by_word, bg='#f0f0f0')
        word_check.pack(side=tk.LEFT, padx=20)
        
        # Input method frame
        input_frame = tk.Frame(self.settings_frame, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Chinese Input Method:", bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.input_method_var = tk.StringVar(value="Direct")
        input_combo = ttk.Combobox(input_frame, textvariable=self.input_method_var, 
                                 values=["Direct", "Zhuyin", "Copy-Paste"], 
                                 state="readonly", width=15)
        input_combo.pack(side=tk.LEFT, padx=10)
        
        # Help button for input method
        help_btn = tk.Button(input_frame, text="Setup Help", command=self.show_input_help,
                           bg='#2196F3', fg='white', font=("Arial", 8))
        help_btn.pack(side=tk.LEFT, padx=10)
        
        # Test button
        test_btn = tk.Button(input_frame, text="Test Mappings", command=self.test_mappings,
                           bg='#FF9800', fg='white', font=("Arial", 8))
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="Start Typing (Ctrl+Shift+S)", 
                                  command=self.start_typing, bg='#4CAF50', fg='white', 
                                  font=("Arial", 12, "bold"), width=20)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="Stop Typing (Ctrl+Shift+X)", 
                                 command=self.stop_typing_action, bg='#f44336', fg='white', 
                                 font=("Arial", 12, "bold"), width=20)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready to type", 
                                    font=("Arial", 10), bg='#f0f0f0', fg='#333')
        self.status_label.pack(pady=10)
    
    def toggle_settings(self):
        """Toggle settings panel visibility"""
        if self.settings_collapsed:
            self.expand_settings()
        else:
            self.collapse_settings()
    
    def collapse_settings(self):
        """Collapse the settings panel"""
        self.settings_collapsed = True
        self.settings_frame.pack_forget()
        self.settings_toggle_btn.config(text="▶ Show Settings")
    
    def expand_settings(self):
        """Expand the settings panel"""
        self.settings_collapsed = False
        self.settings_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.settings_toggle_btn.config(text="▼ Hide Settings")
        
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
        """Load sample text mixing English and Traditional Chinese"""
        sample = """Hello, 你好! 我是一個學生。
        
Today I want to write about 我的家庭. My family consists of 爸爸, 媽媽, and 我.
        
我們住在一個小城市. The weather here is very 好. 我喜歡在這裡學習和工作.
        
In my free time, I like to 看書 and 聽音樂. Sometimes I also 寫作業 or 和朋友聊天.
        
這是一個很好的練習 for typing both English and Traditional Chinese characters naturally."""
        
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert('1.0', sample)
        
    def show_input_help(self):
        """Show input method setup help"""
        help_text = """Input Method Setup Help:

🔧 DIRECT (Recommended):
- Types Chinese characters directly
- Works with any input method
- Most reliable option

🔧 ZHUYIN (IMPROVED):
- Uses traditional Zhuyin (注音) input
- Requires Microsoft Bopomofo IME enabled
- Switch to Chinese input mode first
- More natural but needs proper setup

🔧 COPY-PASTE:
- Uses clipboard to paste characters
- Backup method if others fail
- Slowest but most compatible

IMPORTANT ZHUYIN SETUP:
1. Enable Microsoft Bopomofo IME in Windows
2. Switch to Chinese input (Win+Space)
3. Make sure cursor is in target application
4. Use "Test Mappings" to verify

FOR GOOGLE DOCS:
1. Make sure you can type Chinese manually first
2. Try "Direct" method first
3. If that fails, use "Copy-Paste" method

Windows Setup:
1. Go to Settings > Time & Language > Language
2. Add "Chinese (Traditional, Taiwan)"
3. Install "Microsoft Bopomofo" input method
4. Press Win+Space to switch input methods"""
        
        messagebox.showinfo("Input Method Help", help_text)
        
    def get_typing_delay(self):
        """Get random delay to simulate human typing"""
        return random.uniform(self.min_delay, self.max_delay)
    
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
                time.sleep(self.get_typing_delay())
                return True
            except:
                # Fallback to copy-paste
                pyperclip.copy(chinese_char)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(self.get_typing_delay())
                return True
                
        elif input_method == "Copy-Paste":
            # Use copy-paste method
            try:
                pyperclip.copy(chinese_char)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(self.get_typing_delay())
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
                    time.sleep(self.get_typing_delay())
                    
                    return True
                    
                except Exception as e:
                    print(f"Zhuyin error for '{chinese_char}': {e}")
                    # Fallback to copy-paste
                    try:
                        pyperclip.copy(chinese_char)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(self.get_typing_delay())
                        return True
                    except:
                        return False
            else:
                # No Zhuyin mapping found, use copy-paste
                print(f"No Zhuyin mapping found for '{chinese_char}', using copy-paste")
                try:
                    pyperclip.copy(chinese_char)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(self.get_typing_delay())
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
            'ˊ': '/', '˙': ',', 'ˇ': '-', 'ˋ': '.',
            '': ''  # No tone (first tone)
        }
        
        keys = []
        for char in zhuyin:
            if char in zhuyin_to_key:
                key = zhuyin_to_key[char]
                if key:  # Only add non-empty keys
                    keys.append(key)
            else:
                print(f"Warning: No key mapping for Zhuyin character '{char}'")
        
        return keys
        
    def type_text_word_by_word(self, text):
        """Type text word by word, handling both English and Chinese"""
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
                
            # Process each character in the word
            for i, char in enumerate(word):
                if self.stop_typing:
                    return
                    
                if is_chinese_character(char):
                    # Type Chinese character using selected method
                    if not self.simulate_zhuyin_input(char):
                        return
                else:
                    # Type English character directly
                    pyautogui.write(char)
                    time.sleep(self.get_typing_delay())
                    
            # Add space after word (except for punctuation)
            if word and not word[-1] in '.,!?;:，。！？；：':
                pyautogui.write(' ')
                
            # Pause between words
            time.sleep(self.word_delay)
            
            # Longer pause after sentences
            if word and word[-1] in '.!?。！？':
                time.sleep(self.sentence_delay)
                
    def type_text_character_by_character(self, text):
        """Type text character by character"""
        for char in text:
            if self.stop_typing:
                break
                
            if char == '\n':
                pyautogui.press('enter')
                time.sleep(self.sentence_delay)
            elif char == ' ':
                pyautogui.write(' ')
                time.sleep(self.word_delay)
            elif is_chinese_character(char):
                if not self.simulate_zhuyin_input(char):
                    return
            else:
                pyautogui.write(char)
                time.sleep(self.get_typing_delay())
                
            # Longer pause after sentences
            if char in '.!?。！？':
                time.sleep(self.sentence_delay)
                
    def typing_worker(self):
        """Worker thread for typing"""
        try:
            text = self.text_area.get('1.0', tk.END).strip()
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
        text_widget.config(state='disabled')

if __name__ == "__main__":
    # Disable pyautogui failsafe for better UX (optional)
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
    
    app = AutoTyper()
    app.run() 