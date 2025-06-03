# Auto Typer for Traditional Chinese & English

A sophisticated auto-typing application that can seamlessly type both English and Traditional Chinese characters using Zhuyin (注音) input method or direct character input.

## ✨ Features

- **Mixed Language Support**: Type English and Traditional Chinese characters in the same text
- **Multiple Input Methods**: 
  - Direct character input (recommended)
  - Zhuyin (Bopomofo) input simulation
  - Copy-paste fallback
- **Responsive UI**: Settings automatically collapse on small screens
- **Realistic Typing**: Variable delays and word-by-word typing simulation
- **Global Hotkeys**: Ctrl+Shift+S (start) and Ctrl+Shift+X (stop)
- **Comprehensive Mappings**: 174+ Zhuyin-to-character mappings

## 🚀 Installation

1. **Install Python** (3.7 or higher)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python auto_typer.py
   ```

## 🔧 Setup for Chinese Input

### Method 1: Direct Input (Recommended)
- Works with any Chinese input method already installed
- Most reliable and fastest option
- No additional setup required

### Method 2: Zhuyin Input
1. **Enable Chinese Input**:
   - Go to Windows Settings > Time & Language > Language
   - Add "Chinese (Traditional, Taiwan)"
   - Install "Microsoft Bopomofo" input method

2. **Before using Zhuyin mode**:
   - Switch to Chinese input mode (Win+Space)
   - Make sure the target application can receive Chinese input
   - Test manually first by typing a few Chinese characters

3. **Use the application**:
   - Select "Zhuyin" input method in settings
   - Use "Test Mappings" to verify coverage
   - Click "Start Typing" or use Ctrl+Shift+S

### Method 3: Copy-Paste Fallback
- Slowest but most compatible method
- Works in any application that supports paste
- Automatically used when other methods fail

## 📱 Responsive Design

The application automatically adapts to window size:
- **Large windows**: All settings visible
- **Small windows**: Settings collapse with toggle button
- **Threshold**: 700px width or 500px height

## 🎮 Usage

1. **Enter your text** in the main text area (mix English and Chinese freely)
2. **Choose input method** from the dropdown:
   - **Direct**: Types characters directly (recommended)
   - **Zhuyin**: Uses Bopomofo input simulation
   - **Copy-Paste**: Uses clipboard for Chinese characters
3. **Adjust settings**:
   - **Typing Speed**: Very Slow to Very Fast
   - **Word by word**: Type complete words vs. character by character
4. **Click "Start Typing"** or press **Ctrl+Shift+S**
5. **Switch to target application** within 3 seconds
6. **Stop anytime** with **Ctrl+Shift+X**

## 🧪 Testing

Test the Zhuyin mappings:
```bash
python test_zhuyin.py
```

This will show:
- Character-to-Zhuyin mappings
- Coverage statistics
- Keyboard key conversions

## 🚨 Troubleshooting

### Zhuyin Input Not Working
1. **Verify IME Setup**:
   - Ensure Microsoft Bopomofo is installed
   - Switch to Chinese input mode before starting
   - Test manual typing first

2. **Check Target Application**:
   - Make sure the target app supports Chinese input
   - Try a simple text editor first
   - Avoid protected applications (some games, admin tools)

3. **Use Alternative Methods**:
   - Try "Direct" input method first
   - Use "Copy-Paste" as last resort
   - Check "Test Mappings" for character coverage

### General Issues
- **Characters not typing**: Use "Direct" or "Copy-Paste" method
- **Typing too fast/slow**: Adjust speed in settings
- **Hotkeys not working**: Run as administrator if needed
- **Application freezing**: Close and restart, check target application

### Application-Specific Notes
- **Google Docs**: Works best with "Direct" method
- **Microsoft Word**: All methods supported
- **Games**: May not work due to input protection
- **Protected apps**: Try running auto typer as administrator

## 📊 Mapping Coverage

Current Zhuyin mappings include:
- Basic pronouns and particles (你, 好, 我, 是, 的, etc.)
- Numbers 1-10 plus 百, 千, 萬
- Family terms (爸爸, 媽媽, 家庭, etc.)
- Common verbs (吃, 喝, 看, 聽, 說, 寫, etc.)
- Time expressions (今天, 明天, 昨天, etc.)
- Colors, emotions, and descriptive words
- Technology and modern terms

Total: **174+ character mappings**

## 🔄 Updates in v2

- ✅ **Fixed Zhuyin functionality** with improved keyboard mapping
- ✅ **Responsive UI** that adapts to screen size  
- ✅ **Expanded character mappings** (174+ characters)
- ✅ **Better error handling** and fallback methods
- ✅ **Enhanced testing tools** for mapping verification
- ✅ **Improved help documentation** and setup guides

## 📝 Sample Text

```
Hello, 你好! 我是一個學生。

Today I want to write about 我的家庭. My family consists of 爸爸, 媽媽, and 我.

我們住在一個小城市. The weather here is very 好. 我喜歡在這裡學習和工作.

In my free time, I like to 看書 and 聽音樂. Sometimes I also 寫作業 or 和朋友聊天.

這是一個很好的練習 for typing both English and Traditional Chinese characters naturally.
```

## 🤝 Contributing

Feel free to:
- Add more Zhuyin mappings to `zhuyin_mapping.py`
- Report bugs or suggest improvements
- Test with different applications and input methods

## ⚠️ Disclaimer

This tool is for educational and productivity purposes. Be mindful of:
- Terms of service for online platforms
- Academic integrity policies
- Appropriate use in professional settings

---

**Version**: 2.0  
**Author**: Auto Typer Team  
**License**: MIT 