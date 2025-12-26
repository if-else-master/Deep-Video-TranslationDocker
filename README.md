# Deep Video Translation 🎥

## 概述

AI驅動的高保真視頻翻譯系統，集成最先進的語音、視覺和語言模型。

### 核心功能

- **🎙️ ASR (語音識別)**: Faster-Whisper - 高精度語音轉文字
- **🧠 翻譯**: Gemini/OpenAI/Ollama - 多語言LLM翻譯
- **🗣️ TTS (語音合成)**: F5-TTS - 高質量語音克隆
- **👄 唇形同步**: Wav2Lip - 音頻驅動的精確唇形匹配
- **🧼 OCR/Inpaint (可選)**: EasyOCR + OpenCV - 智能字幕移除
- **⏱️ 時間軸對齊**: 自動音頻拉伸匹配原視頻長度

### 技術棧

- **前端**: Streamlit Web UI
- **深度學習框架**: PyTorch (支援 CUDA/MPS/CPU)
- **音頻處理**: librosa, pyrubberband, pydub
- **視覺處理**: OpenCV, EasyOCR
- **優化**: 記憶體管理，模型動態加載/卸載

### 硬件需求

- **推薦**: Mac M4 Pro (24GB RAM) 或 NVIDIA GPU (8GB+ VRAM)
- **最低**: 16GB RAM, CPU (較慢)

---

## 快速開始

### 1. 環境準備

#### Mac (推薦)

```bash
# 安裝系統依賴
brew install rubberband ffmpeg

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

#### Linux/Windows

```bash
# Linux: 安裝系統依賴
sudo apt-get install ffmpeg
# 安裝 rubberband (可選，用於更好的音頻拉伸)
sudo apt-get install rubberband-cli

# Windows: 下載並安裝 ffmpeg
# https://ffmpeg.org/download.html

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 下載模型

模型會在首次運行時自動下載，或手動下載：

#### F5-TTS (自動下載)
首次使用時會自動從 HuggingFace 下載

#### Wav2Lip
模型已包含在 `Wav2Lip/checkpoints/` 目錄：
- `wav2lip.pth` - 基礎模型 (高精度唇形)
- `wav2lip_gan.pth` - GAN模型 (更好的視覺質量)

#### EasyOCR (自動下載)
首次使用時會自動下載到 `~/.EasyOCR/`

### 3. 運行

```bash
# 激活虛擬環境
source venv/bin/activate

# 啟動 Streamlit 應用
streamlit run app.py
```

應用會在瀏覽器中打開 `http://localhost:8501`

---

## 使用說明

### 基本流程

1. **配置 LLM**
   - 選擇 LLM 提供商（Gemini/OpenAI/Ollama）
   - 輸入 API Key（Gemini/OpenAI 需要）
   - 選擇目標語言

2. **上傳視頻**
   - 支援格式：MP4, MOV, AVI
   - 推薦分辨率：720p-1080p

3. **選擇選項**
   - ✅ 啟用 OCR/Inpaint：移除原視頻字幕
   - ✅ 啟用音頻時間拉伸：自動匹配原視頻長度

4. **開始處理**
   - 點擊「開始翻譯處理」
   - 等待處理完成（約 2-5 分鐘/分鐘視頻）
   - 下載翻譯後的視頻

### 處理流程

```
原視頻 
  ↓
[ASR] Faster-Whisper 轉錄
  ↓
[LLM] 翻譯文本
  ↓
[TTS] F5-TTS 生成翻譯語音（克隆原聲）
  ↓
[時間拉伸] 匹配原視頻長度
  ↓
[OCR] 檢測並移除字幕（可選）
  ↓
[Lip-Sync] Wav2Lip 同步唇形
  ↓
翻譯後視頻 ✨
```

---

## 進階配置

### API Keys

#### Gemini (推薦)
```bash
export GEMINI_API_KEY="your-api-key"
```
獲取: https://makersuite.google.com/app/apikey

#### OpenAI
```bash
export OPENAI_API_KEY="your-api-key"
```
獲取: https://platform.openai.com/api-keys

#### Ollama (本地)
```bash
# 安裝 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下載模型
ollama pull llama3

# 運行（默認端口 11434）
ollama serve
```

### 模型選擇

#### Wav2Lip 模型對比

| 模型 | 唇形精度 | 視覺質量 | 速度 |
|------|---------|---------|------|
| `wav2lip.pth` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 快 |
| `wav2lip_gan.pth` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 較慢 |

修改 `modules/visual_sync.py` 第 18 行切換模型。

---

## 專案結構

```
Deep-Video-TranslationDocker/
├── app.py                    # Streamlit 主應用
├── requirements.txt          # Python 依賴
├── core/                     # 核心模組
│   ├── config.py            # 配置管理
│   ├── device_manager.py    # GPU/CPU 管理
│   └── logger.py            # 日誌系統
├── modules/                  # 處理模組
│   ├── asr_llm.py           # ASR + LLM 翻譯
│   ├── audio_tts.py         # F5-TTS 語音合成
│   ├── visual_sync.py       # Wav2Lip 唇形同步
│   └── ocr_inpaint.py       # OCR 字幕移除
├── F5-TTS/                   # F5-TTS 子模組
├── Wav2Lip/                  # Wav2Lip 子模組
│   └── checkpoints/         # 預訓練模型
└── temp/                     # 臨時文件目錄
```

---

## 故障排除

### 常見問題

#### 1. `pyrubberband` 安裝失敗
```bash
# Mac
brew install rubberband

# Linux
sudo apt-get install rubberband-cli

# 如果仍然失敗，使用備選方案 audiotsm（已包含在 requirements.txt）
```

#### 2. EasyOCR 下載慢
```bash
# 使用鏡像加速
pip install easyocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. Wav2Lip 人臉檢測失敗
- 確保視頻中人臉清晰可見
- 嘗試降低分辨率（720p）
- 調整 `--pads` 參數擴大檢測範圍

#### 4. 記憶體不足 (OOM)
- 降低視頻分辨率
- 處理較短的視頻片段
- 使用 CPU 模式（較慢但記憶體需求低）

#### 5. Mac M4 Pro MPS 錯誤
某些模組可能不完全支援 MPS，系統會自動降級到 CPU。

---

## 更新日誌

### v2.0.0 - 2024-12-24

✅ **重大修復**
- 將 LivePortrait 替換為 Wav2Lip（修復唇形同步）
- 實現 EasyOCR/OpenCV 的 OCR/Inpaint 功能
- 添加音頻時間拉伸功能（匹配原視頻長度）
- 修復 TTS ref_text 參數傳遞

🎉 **新功能**
- 支援多語言 OCR（中英日韓）
- 自動記憶體管理和模型卸載
- 改進的 UI 和錯誤處理
- 視頻時長檢測和進度顯示

🔧 **技術改進**
- 使用 pyrubberband 進行高質量音頻拉伸
- 優化設備管理（CUDA/MPS/CPU）
- 更好的日誌和調試信息

### v1.0.0 - Initial Release
- 基礎功能實現

---

## 性能優化建議

### 處理速度優化

1. **使用 GPU**: CUDA > MPS > CPU
2. **降低分辨率**: 720p 比 1080p 快 2-3 倍
3. **跳過 OCR**: 如果沒有字幕可跳過
4. **批量處理**: 使用腳本批量處理多個視頻

### 質量優化

1. **高質量語音參考**: 使用清晰的前 10 秒音頻
2. **人臉清晰**: Wav2Lip 需要清晰的正臉
3. **翻譯質量**: 使用 GPT-4 或 Gemini Pro 以獲得更好翻譯
4. **時間拉伸限制**: 避免超過 2倍 的拉伸比率

---

## 開發計劃

- [ ] 支援批量處理多個視頻
- [ ] 添加視頻預覽和編輯功能
- [ ] 支援更多語言和方言
- [ ] Docker 容器化部署
- [ ] API 服務模式
- [ ] 實時視頻流處理

---

## 授權

本專案僅供研究和個人使用。

### 第三方組件授權

- **F5-TTS**: MIT License
- **Wav2Lip**: 僅限非商業使用
- **EasyOCR**: Apache 2.0 License
- **Faster-Whisper**: MIT License

**重要**: Wav2Lip 訓練於 LRS2 數據集，嚴禁商業用途。

---

## 致謝

- [F5-TTS](https://github.com/SWivid/F5-TTS) - 高質量語音合成
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) - 唇形同步
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR 引擎
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - ASR 引擎

---

## 聯繫與支持

如有問題或建議，請提交 Issue 或 Pull Request。

**Enjoy translating! 🎉**
