# 🚀 快速啟動指南

## ✅ 系統狀態

**所有模組已修復並測試通過！** (15/15 測試通過)

---

## 📋 修復內容總結

### 🔴 嚴重 Bug 已修復

| # | 問題 | 狀態 | 解決方案 |
|---|------|------|---------|
| 1 | **Lip-Sync 功能無法運作** | ✅ 已修復 | 將 LivePortrait 替換為 Wav2Lip |
| 2 | **OCR/Inpaint 未實現** | ✅ 已實現 | 使用 EasyOCR + OpenCV |
| 3 | **音頻時間軸不對齊** | ✅ 已修復 | 添加時間拉伸功能 |
| 4 | **TTS ref_text 缺失** | ✅ 已修復 | 自動提取前10秒原文 |

### ✨ 新功能

- 🌐 多語言 OCR 支援（中英日韓）
- ⏱️ 自動音頻時間拉伸
- 🎨 改進的中文 UI
- 📊 實時進度顯示
- 📥 一鍵下載翻譯視頻

---

## 🏃 立即開始

### 1️⃣ 激活環境

```bash
cd /Users/raychang/Documents/專案/Deep-Video-TranslationDocker
source .venv/bin/activate
```

### 2️⃣ 啟動應用

```bash
streamlit run app.py
```

應用將在瀏覽器中打開：`http://localhost:8501`

### 3️⃣ 配置 API Key

在側邊欄選擇 LLM 提供商並輸入 API Key：

#### 選項 A：Gemini (推薦，免費額度)
```bash
# 獲取 API Key: https://makersuite.google.com/app/apikey
# 在 UI 中輸入或設置環境變量：
export GEMINI_API_KEY="your-api-key"
```

#### 選項 B：OpenAI
```bash
# 獲取 API Key: https://platform.openai.com/api-keys
export OPENAI_API_KEY="your-api-key"
```

#### 選項 C：Ollama (本地免費)
```bash
# 安裝 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下載模型
ollama pull llama3

# 運行（會在後台自動啟動）
ollama serve
```

---

## 📝 使用流程

### 基本步驟

1. **上傳視頻** 📹
   - 支援格式：MP4, MOV, AVI
   - 推薦分辨率：720p-1080p
   - 推薦長度：< 5 分鐘（首次測試）

2. **選擇目標語言** 🌍
   - 繁體中文
   - 簡體中文
   - 英文
   - 日文
   - 韓文

3. **配置選項** ⚙️
   - ✅ **啟用 OCR/Inpaint**: 移除原視頻字幕
   - ✅ **啟用音頻時間拉伸**: 自動匹配原視頻長度

4. **開始處理** 🚀
   - 點擊「開始翻譯處理」
   - 等待 5 個步驟完成：
     1. 🎙️ ASR & 翻譯
     2. 🗣️ 語音合成
     3. 🧼 字幕移除（可選）
     4. 👄 唇形同步
     5. ✅ 完成

5. **下載結果** 📥
   - 預覽翻譯後的視頻
   - 點擊「下載翻譯視頻」

---

## ⚡ 性能說明

### 處理時間估算

| 視頻長度 | Mac M4 Pro (MPS) | NVIDIA RTX 3090 | CPU (Intel i7) |
|---------|------------------|-----------------|----------------|
| 1 分鐘   | ~2-3 分鐘 ⚡     | ~1-2 分鐘 ⚡⚡  | ~5-8 分鐘 🐢   |
| 5 分鐘   | ~10-15 分鐘      | ~5-8 分鐘       | ~25-40 分鐘    |

### 記憶體需求

- **推薦**: 24GB RAM
- **最低**: 16GB RAM
- **GPU VRAM**: 8GB+ (可選)

---

## 🔍 驗證測試

### 運行測試

```bash
python test_imports.py
```

**預期輸出**:
```
============================================================
測試核心模組...
============================================================
✅ Core: Device Manager
✅ Core: Logger
✅ Core: Config
✅ Module: ASR/LLM
✅ Module: TTS
✅ Module: Visual Sync
✅ Module: OCR/Inpaint
✅ Dependency: EasyOCR
✅ Dependency: pyrubberband
✅ Dependency: audiotsm
...

通過: 15/15

🎉 所有測試通過！系統準備就緒。
```

---

## 🐛 故障排除

### 常見問題

#### 1. 應用無法啟動
```bash
# 確保虛擬環境已激活
source .venv/bin/activate

# 重新安裝依賴
pip install -r requirements.txt
```

#### 2. 人臉檢測失敗
- 確保視頻中人臉清晰
- 嘗試使用 720p 分辨率
- 確保光線充足

#### 3. 記憶體不足
```bash
# 降低視頻分辨率
# 或處理較短的片段
# 或關閉 OCR/Inpaint 功能
```

#### 4. API Key 錯誤
```bash
# 檢查 API Key 是否正確
# Gemini: https://makersuite.google.com/app/apikey
# OpenAI: https://platform.openai.com/api-keys
```

#### 5. 模型下載慢
```bash
# F5-TTS 和 EasyOCR 首次使用會自動下載
# 耐心等待或使用代理
export HF_ENDPOINT=https://hf-mirror.com  # 國內加速
```

---

## 📚 進階使用

### 調整 Wav2Lip 模型

編輯 `modules/visual_sync.py` 第 18 行：

```python
# 使用 GAN 模型（更好的視覺質量）
self.checkpoint_path = str(WAV2LIP_PATH / "checkpoints" / "wav2lip_gan.pth")

# 或使用基礎模型（更好的唇形精度）
self.checkpoint_path = str(WAV2LIP_PATH / "checkpoints" / "wav2lip.pth")
```

### 批量處理

創建批量處理腳本（未來功能）：

```python
# TODO: 實現批量處理
from modules.asr_llm import ASRLLMPipeline
from modules.audio_tts import TTSProcessor
from modules.visual_sync import VisualSyncProcessor
# ...
```

---

## 📖 文檔

- **README.md**: 完整文檔
- **CHANGELOG.md**: 更新日誌
- **QUICKSTART.md**: 本文件

---

## 🎉 開始使用！

```bash
# 1. 激活環境
source .venv/bin/activate

# 2. 啟動應用
streamlit run app.py

# 3. 在瀏覽器中打開 http://localhost:8501

# 4. 上傳視頻並開始翻譯！
```

**祝您使用愉快！** 🚀

如有問題，請查看 README.md 或提交 Issue。

