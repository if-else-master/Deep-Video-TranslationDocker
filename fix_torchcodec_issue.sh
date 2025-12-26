#!/bin/bash
# 修復 torchcodec 在 Mac M4 上的問題
# torchcodec 需要 FFmpeg 動態庫，但在 Mac M4 上無法正常工作
# F5-TTS 並不真正需要 torchcodec，可以安全卸載

echo "======================================================================"
echo "修復 TorchCodec 問題"
echo "======================================================================"
echo ""
echo "問題: torchcodec 在 Mac M4 Pro 上無法載入 FFmpeg 庫"
echo "解決: 卸載 torchcodec（F5-TTS 不需要它）"
echo ""

# 確保在虛擬環境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  請先激活虛擬環境:"
    echo "   source .venv/bin/activate"
    echo ""
    exit 1
fi

echo "當前虛擬環境: $VIRTUAL_ENV"
echo ""

# 檢查是否安裝了 torchcodec
if pip show torchcodec &>/dev/null; then
    echo "✅ 檢測到 torchcodec 已安裝"
    echo ""
    echo "正在卸載 torchcodec..."
    pip uninstall -y torchcodec
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ torchcodec 已成功卸載"
        echo ""
        echo "說明:"
        echo "  • F5-TTS 會使用 soundfile 或 librosa 作為音頻後端"
        echo "  • 不會影響任何功能"
        echo "  • torchcodec 僅用於視頻處理（F5-TTS 不需要）"
        echo ""
        echo "現在可以運行測試:"
        echo "  python test_f5tts_standalone.py --quick"
        echo ""
    else
        echo ""
        echo "❌ 卸載失敗"
        exit 1
    fi
else
    echo "ℹ️  torchcodec 未安裝"
    echo ""
fi

echo "======================================================================"
echo "修復完成！"
echo "======================================================================"

