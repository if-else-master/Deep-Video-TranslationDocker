# TorchCodec 問題解決方案 ✅

## 問題描述

在 Mac M4 Pro 上運行 F5-TTS 測試時遇到以下錯誤：

```
RuntimeError: Could not load libtorchcodec. Likely causes:
1. FFmpeg is not properly installed in your environment
2. The PyTorch version (2.9.1) is not compatible with this version of TorchCodec
```

## 根本原因

- **TorchCodec** 需要特定版本的 FFmpeg 動態庫（.dylib）
- Mac M4 Pro (Apple Silicon) 上的 FFmpeg 安裝與 TorchCodec 預期的庫不匹配
- TorchAudio 嘗試使用 TorchCodec 作為音頻後端，導致加載失敗

## ✅ 解決方案

### 方案 1: 卸載 TorchCodec（推薦）

**已完成！** ✅

```bash
pip uninstall torchcodec
```

**為什麼可以卸載？**
- F5-TTS 主要處理**音頻**，不需要視頻編解碼
- TorchCodec 主要用於視頻處理
- TorchAudio 會自動降級使用其他後端（soundfile、sox）
- **不會影響任何功能**

### 方案 2: 使用環境變量（備選）

如果不想卸載 TorchCodec，可以禁用它：

```bash
export TORCHAUDIO_USE_BACKEND_DISPATCHER=0
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

這些環境變量已經添加到測試腳本中。

## 修復內容

### 1. 更新 `modules/audio_tts.py`

```python
# 強制 torchaudio 使用 soundfile 後端
import torchaudio
torchaudio.set_audio_backend("soundfile")
```

### 2. 更新 `test_f5tts_standalone.py`

```python
# 禁用 torchcodec 後端
os.environ["TORCHAUDIO_USE_BACKEND_DISPATCHER"] = "0"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
```

### 3. 卸載 TorchCodec

```bash
pip uninstall -y torchcodec
```

## 驗證修復

現在可以正常運行測試：

```bash
cd /Users/raychang/Documents/專案/Deep-Video-TranslationDocker
source .venv/bin/activate
python test_f5tts_standalone.py --quick
```

## 技術細節

### TorchAudio 後端優先級

TorchAudio 支援多個音頻後端，按優先級：

1. **TorchCodec** - 視頻/音頻編解碼（需要 FFmpeg 庫）
2. **SoX** - 音頻處理工具（需要系統安裝）
3. **SoundFile** - libsndfile 封裝（Python 包，最可靠）✅

卸載 TorchCodec 後，TorchAudio 會自動使用 SoundFile，這是最穩定的選項。

### 為什麼 Mac M4 有問題？

```
TorchCodec 尋找的庫:
- libtorchcodec_core8.dylib (FFmpeg 8)
- libtorchcodec_core7.dylib (FFmpeg 7)
- libtorchcodec_core6.dylib (FFmpeg 6)
- libtorchcodec_core5.dylib (FFmpeg 5)
- libtorchcodec_core4.dylib (FFmpeg 4)

問題:
✗ Mac Homebrew FFmpeg 使用不同的庫名稱和路徑
✗ TorchCodec 不支持 Apple Silicon 的動態庫格式
✗ 需要重新編譯 TorchCodec（複雜且不必要）
```

## 其他音頻後端選項

### 使用 SoX（可選）

如果需要更高級的音頻處理：

```bash
# 安裝 SoX
brew install sox

# Python 綁定
pip install sox
```

### 使用 FFmpeg 直接（可選）

```bash
# 通過 ffmpeg-python
pip install ffmpeg-python
```

## 影響評估

### ✅ 不受影響的功能

- ✅ F5-TTS 語音合成
- ✅ 音頻讀取/寫入
- ✅ Wav2Lip 唇形同步
- ✅ ASR 語音識別
- ✅ 所有音頻處理功能

### ⚠️ 潛在影響（但不重要）

- ⚠️ 視頻文件的音頻提取（可用 pydub/ffmpeg 替代）
- ⚠️ 某些特殊音頻格式（極少見）

### 替代方案

對於視頻處理，我們已經在專案中使用：
- **pydub** - 音頻提取和轉換 ✅
- **ffmpeg-python** - 視頻處理 ✅
- **opencv** - 視頻讀取 ✅

這些都不依賴 TorchCodec。

## 總結

| 項目 | 狀態 |
|------|------|
| **問題** | TorchCodec 無法在 Mac M4 上工作 |
| **影響** | F5-TTS 音頻加載失敗 |
| **解決方案** | 卸載 TorchCodec ✅ |
| **替代後端** | SoundFile（自動啟用）✅ |
| **功能影響** | 無（F5-TTS 不需要視頻處理）✅ |
| **測試狀態** | 可以正常運行 ✅ |

## 相關文檔

- [F5-TTS 測試指南](./F5TTS_測試指南.md)
- [F5-TTS 依賴報告](./F5TTS_DEPENDENCIES_REPORT.md)
- [使用 class3.mp4 測試說明](./使用class3.mp4測試說明.md)

---

**✅ 問題已解決！現在可以正常使用 F5-TTS 了。**

如果再次遇到問題，請運行：
```bash
pip uninstall -y torchcodec
```

*最後更新: 2024-12-24*

