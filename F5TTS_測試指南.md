# F5-TTS 獨立測試指南 🎤

## 📝 概述

這個測試腳本 (`test_f5tts_standalone.py`) 可以**完全不需要任何外部 API**（如 Gemini、OpenAI）來測試 F5-TTS 語音合成功能。

### ✨ 特點

- ✅ **無需 API Key** - 純本地運行
- ✅ **自動創建測試音頻** - 不需要準備參考音頻
- ✅ **多種測試案例** - 中文、英文、混合、長文本
- ✅ **三種測試模式** - 完整測試、快速測試、自定義測試

---

## 🚀 快速開始

### 1. 快速測試（推薦首次使用）

最快的測試方式，只測試一個簡單案例：

```bash
cd /Users/raychang/Documents/專案/Deep-Video-TranslationDocker
source .venv/bin/activate
python test_f5tts_standalone.py --quick
```

**預期輸出**:
```
F5-TTS 快速測試
參考文字: 這是參考音頻。
生成文字: 你好，這是一個快速測試。

載入 F5-TTS...
生成語音...
✅ 成功！
   輸出: /path/to/temp/quick_test_output.wav
   大小: 45.3 KB

播放命令: afplay /path/to/temp/quick_test_output.wav
```

**時間**: 首次約 2-5 分鐘（需下載模型），之後約 10-30 秒

---

### 2. 完整測試

測試所有預設案例（中文、英文、混合、長文本）：

```bash
python test_f5tts_standalone.py
```

**測試案例**:
1. ✅ 中文測試 - "大家好，我是 F5-TTS 語音合成系統..."
2. ✅ 英文測試 - "Hello everyone, I am F5-TTS..."
3. ✅ 中英混合 - "歡迎使用 F5-TTS，這是一個強大的 text-to-speech..."
4. ✅ 長文本測試 - 約 100 字的段落

**時間**: 約 5-10 分鐘

---

### 3. 自定義文字測試

測試您自己的文字：

```bash
python test_f5tts_standalone.py --text "您想要測試的任何文字"
```

**範例**:

```bash
# 中文
python test_f5tts_standalone.py --text "今天天氣很好，適合出去走走。"

# 英文
python test_f5tts_standalone.py --text "The weather is nice today."

# 中英混合
python test_f5tts_standalone.py --text "這是一個 AI 語音合成系統。"

# 長文本
python test_f5tts_standalone.py --text "$(cat your_text_file.txt)"
```

---

## 📋 內建測試文本

### 測試案例 1: 中文測試

**參考文字**: `這是一段參考音頻的文字，用來克隆聲音。`

**生成文字**: 
```
大家好，我是 F5-TTS 語音合成系統。
今天天氣很好，適合出去走走。
```

---

### 測試案例 2: 英文測試

**參考文字**: `This is a reference audio text for voice cloning.`

**生成文字**:
```
Hello everyone, I am F5-TTS text to speech system. 
The weather is nice today.
```

---

### 測試案例 3: 中英混合

**參考文字**: `這是參考音頻，包含中文和 English。`

**生成文字**:
```
歡迎使用 F5-TTS，這是一個強大的 text-to-speech 系統，
支持多語言。
```

---

### 測試案例 4: 長文本測試

**生成文字**:
```
F5-TTS 是一個基於流匹配的語音合成系統，它可以實現高質量的語音克隆。
通過提供參考音頻和參考文字，系統能夠學習說話人的聲音特徵，
然後生成任意文字的語音，並保持原有的音色和風格。
這項技術在視頻配音、有聲書製作、虛擬助手等領域有廣泛應用。
```

---

## 🎧 播放生成的音頻

### macOS

```bash
# 播放單個文件
afplay temp/test_output_中文測試.wav

# 播放所有測試輸出
afplay temp/test_output_*.wav
```

### Linux

```bash
# 使用 aplay
aplay temp/test_output_*.wav

# 或使用 mpv
mpv temp/test_output_*.wav
```

### Windows

```bash
# 使用 Windows Media Player
start temp\test_output_中文測試.wav
```

### 或直接用文件管理器

```bash
# macOS
open temp/

# Linux
xdg-open temp/

# Windows
explorer temp\
```

---

## 📊 測試輸出

### 輸出目錄

所有測試文件都保存在 `temp/` 目錄：

```
temp/
├── test_ref_audio.wav              # 參考音頻
├── test_output_中文測試.wav         # 中文測試輸出
├── test_output_英文測試.wav         # 英文測試輸出
├── test_output_中英混合.wav         # 混合測試輸出
├── test_output_長文本測試.wav       # 長文本測試輸出
├── quick_test_ref.wav              # 快速測試參考音頻
└── quick_test_output.wav           # 快速測試輸出
```

### 輸出格式

- **格式**: WAV
- **採樣率**: 24000 Hz
- **位深度**: 16-bit
- **聲道**: 單聲道

---

## 🔧 參考音頻說明

### 自動創建的參考音頻

腳本會自動創建參考音頻：

#### 選項 1: 系統語音（推薦，僅 Mac）

```python
# 使用 macOS 系統 TTS (Tingting 中文女聲)
say -v Tingting -o ref.aiff "參考文字"
```

**優點**: 
- ✅ 真實人聲
- ✅ 音質好
- ✅ 自然流暢

#### 選項 2: 合成音頻（備選）

```python
# 多頻率混合正弦波
f1=200Hz, f2=300Hz, f3=400Hz
```

**優點**:
- ✅ 跨平台
- ✅ 不需要額外工具
- ✅ 快速生成

**缺點**:
- ⚠️ 音質較差（不是真實人聲）
- ⚠️ 克隆效果可能不佳

---

### 使用您自己的參考音頻

如果您想使用自己的參考音頻（推薦）：

```python
# 修改腳本或直接使用
from modules.audio_tts import TTSProcessor

tts = TTSProcessor()
tts.generate_audio(
    text="要生成的文字",
    ref_audio="your_voice.wav",  # 您的音頻文件
    output_path="output.wav",
    ref_text="您音頻對應的文字"  # 重要！提升質量
)
```

**參考音頻要求**:
- ✅ 格式: WAV, MP3, FLAC 等
- ✅ 長度: 3-10 秒最佳
- ✅ 質量: 清晰、無噪音
- ✅ 內容: 單人說話

---

## ⚙️ 性能說明

### 首次運行

```
載入 F5-TTS...
註: 首次運行會下載模型（~500MB），請耐心等待...
下載中... [████████████████████] 100%
模型載入中...
✅ 完成
```

**時間**: 2-5 分鐘（取決於網速）  
**空間**: ~500MB

### 後續運行

```
載入 F5-TTS...
✅ 完成
```

**時間**: 10-30 秒  
**記憶體**: ~2-4GB

### 生成速度

| 文本長度 | Mac M4 (MPS) | NVIDIA RTX 3090 | CPU (i7) |
|---------|--------------|-----------------|----------|
| 短文本 (20字) | ~5秒 ⚡ | ~3秒 ⚡⚡ | ~15秒 🐢 |
| 中文本 (50字) | ~10秒 ⚡ | ~5秒 ⚡⚡ | ~30秒 🐢 |
| 長文本 (100字) | ~20秒 ⚡ | ~10秒 ⚡⚡ | ~60秒 🐢 |

---

## 🐛 故障排除

### Q: 首次運行很慢？

**A**: 正常！需要下載模型（~500MB）

```bash
# 檢查下載進度
ls -lh ~/.cache/huggingface/hub/models--*F5*
```

---

### Q: 記憶體不足錯誤

**A**: 
```bash
# 1. 確保至少 8GB 可用 RAM
free -h  # Linux
vm_stat  # macOS

# 2. 關閉其他應用
# 3. 使用較短的文本測試
python test_f5tts_standalone.py --text "短文本"
```

---

### Q: 音頻質量不好？

**A**: 
1. **使用真實人聲作為參考音頻**（推薦）
2. **提供準確的 ref_text**
3. **參考音頻要清晰**

```bash
# 在 Mac 上創建更好的參考音頻
say -v Tingting -o my_ref.aiff "這是參考文字"
ffmpeg -i my_ref.aiff -ar 24000 my_ref.wav

# 然後修改腳本使用這個音頻
```

---

### Q: 生成的音頻沒有聲音？

**A**: 
```bash
# 檢查文件大小
ls -lh temp/test_output_*.wav

# 如果文件很小 (< 10KB)，可能生成失敗
# 查看錯誤日誌
python test_f5tts_standalone.py 2>&1 | tee test.log
```

---

### Q: MPS (Mac M4) 不工作？

**A**:
```python
# 檢查 PyTorch MPS 支援
python -c "import torch; print(torch.backends.mps.is_available())"

# 如果返回 False，使用 CPU
# 在腳本中會自動降級到 CPU
```

---

## 💡 使用技巧

### 1. 準備高質量參考音頻

```bash
# 錄製您自己的聲音 (3-10 秒)
# macOS QuickTime: 文件 > 新建音頻錄製
# 或使用 Audacity

# 轉換為 WAV
ffmpeg -i recording.m4a -ar 24000 -ac 1 ref_audio.wav
```

### 2. 批量測試

```bash
# 創建測試文本文件
cat > test_texts.txt << EOF
這是第一個測試文本
這是第二個測試文本
這是第三個測試文本
EOF

# 批量測試
while read line; do
    python test_f5tts_standalone.py --text "$line"
done < test_texts.txt
```

### 3. 比較不同模型

```python
# 修改 modules/audio_tts.py
# 測試不同的 F5-TTS 模型

models = ['F5TTS_v1_Base', 'F5TTS_Small', 'E2TTS_Base']
for model in models:
    tts = TTSProcessor()
    # 修改 model 參數...
```

---

## 📚 相關文檔

- [F5-TTS GitHub](https://github.com/SWivid/F5-TTS)
- [專案 README](./README.md)
- [F5-TTS 依賴報告](./F5TTS_DEPENDENCIES_REPORT.md)
- [F5-TTS 安裝總結](./F5TTS_安裝總結.md)

---

## 🎯 測試檢查清單

在正式使用前，建議完成以下測試：

- [ ] 快速測試通過
- [ ] 中文測試通過
- [ ] 英文測試通過
- [ ] 能播放生成的音頻
- [ ] 音頻質量可接受
- [ ] 生成速度可接受
- [ ] 記憶體使用正常

---

## ✅ 總結

### 推薦測試流程

```bash
# 1. 快速測試（確認功能）
python test_f5tts_standalone.py --quick

# 2. 播放測試結果
afplay temp/quick_test_output.wav

# 3. 如果滿意，運行完整測試
python test_f5tts_standalone.py

# 4. 測試自定義文本
python test_f5tts_standalone.py --text "您的文字"
```

### 下一步

如果測試通過，您可以：
1. ✅ 在主應用中使用 F5-TTS
2. ✅ 開始視頻翻譯項目
3. ✅ 準備真實的參考音頻
4. ✅ 調整生成參數優化質量

**祝測試順利！** 🎉

---

*最後更新: 2024-12-24*

