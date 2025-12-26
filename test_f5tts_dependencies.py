#!/usr/bin/env python3
"""
F5-TTS 依賴測試腳本
測試所有 F5-TTS 所需的 Python 模組是否已正確安裝
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_module(module_name, import_statement=None, description=""):
    """
    測試單個模組是否可以導入
    
    Args:
        module_name: 模組名稱（用於顯示）
        import_statement: 實際的導入語句，如果為 None 則使用 "import {module_name}"
        description: 模組描述
    
    Returns:
        (success: bool, error_msg: str or None)
    """
    if import_statement is None:
        import_statement = f"import {module_name}"
    
    try:
        exec(import_statement)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"其他錯誤: {str(e)}"

def main():
    """主測試函數"""
    print("=" * 80)
    print("F5-TTS 依賴測試")
    print("=" * 80)
    print()
    
    # 定義所有需要測試的依賴
    # 格式: (顯示名稱, 導入語句, 描述, 是否必需)
    dependencies = [
        # PyTorch 核心
        ("torch", "import torch", "PyTorch 深度學習框架", True),
        ("torchaudio", "import torchaudio", "PyTorch 音頻處理", True),
        ("torchvision", "import torchvision", "PyTorch 視覺處理", True),
        
        # F5-TTS 核心依賴
        ("accelerate", "import accelerate", "HuggingFace 加速庫", True),
        ("cached_path", "import cached_path", "文件緩存管理", True),
        ("click", "import click", "命令行工具", True),
        ("datasets", "import datasets", "HuggingFace 數據集", True),
        ("ema_pytorch", "import ema_pytorch", "EMA 訓練技術", True),
        ("gradio", "import gradio", "Web UI 框架", True),
        ("hydra-core", "import hydra", "配置管理", True),
        
        # 音頻處理
        ("librosa", "import librosa", "音頻分析庫", True),
        ("soundfile", "import soundfile", "音頻文件讀寫", True),
        ("pydub", "import pydub", "音頻處理", True),
        ("vocos", "import vocos", "神經聲碼器", True),
        
        # 數值計算和可視化
        ("numpy", "import numpy", "數值計算", True),
        ("matplotlib", "import matplotlib", "數據可視化", True),
        ("scipy", "import scipy", "科學計算", True),
        
        # Transformers 相關
        ("transformers", "import transformers", "HuggingFace Transformers", True),
        ("transformers_stream_generator", "import transformers_stream_generator", "流式生成器", True),
        ("x_transformers", "import x_transformers", "擴展 Transformers", True),
        
        # 文本處理
        ("pypinyin", "import pypinyin", "中文拼音轉換", True),
        ("rjieba", "import rjieba", "中文分詞（Rust版）", True),
        ("unidecode", "import unidecode", "Unicode 轉 ASCII", True),
        
        # 模型和訓練
        ("safetensors", "import safetensors", "安全張量存儲", True),
        ("pydantic", "import pydantic", "數據驗證", True),
        ("tqdm", "import tqdm", "進度條", True),
        ("wandb", "import wandb", "實驗跟踪", True),
        
        # 特殊依賴
        ("torchcodec", "import torchcodec", "視頻編解碼", True),
        ("torchdiffeq", "import torchdiffeq", "微分方程求解器", True),
        ("tomli", "import tomli", "TOML 解析器", True),
        
        # Mac/Linux 條件依賴
        ("bitsandbytes", "import bitsandbytes", "量化訓練（非 Mac ARM）", False),
        
        # F5-TTS 內部模組
        ("f5_tts.api", "from f5_tts.api import F5TTS", "F5-TTS API", True),
        ("f5_tts.model", "from f5_tts.model import CFM", "F5-TTS 模型", True),
        ("f5_tts.infer.utils_infer", "from f5_tts.infer.utils_infer import load_model", "推理工具", True),
    ]
    
    # 可選依賴（評估用）
    optional_dependencies = [
        ("faster_whisper", "import faster_whisper", "ASR 引擎（評估）", False),
        ("funasr", "import funasr", "阿里 ASR（評估）", False),
        ("jiwer", "import jiwer", "WER 計算（評估）", False),
        ("modelscope", "import modelscope", "ModelScope（評估）", False),
        ("zhconv", "import zhconv", "簡繁轉換（評估）", False),
        ("zhon", "import zhon", "中文常量（評估）", False),
    ]
    
    # 執行測試
    results = {
        "必需依賴": [],
        "可選依賴": []
    }
    
    print("📦 測試必需依賴...")
    print("-" * 80)
    
    for name, import_stmt, desc, required in dependencies:
        success, error = test_module(name, import_stmt, desc)
        
        status = "✅" if success else "❌"
        required_mark = "【必需】" if required else "【可選】"
        
        print(f"{status} {required_mark} {name:30s} - {desc}")
        
        if not success and error:
            print(f"   錯誤: {error}")
        
        results["必需依賴"].append({
            "name": name,
            "description": desc,
            "required": required,
            "success": success,
            "error": error
        })
    
    print()
    print("📦 測試可選依賴（用於評估/訓練）...")
    print("-" * 80)
    
    for name, import_stmt, desc, required in optional_dependencies:
        success, error = test_module(name, import_stmt, desc)
        
        status = "✅" if success else "⚠️ "
        
        print(f"{status} {name:30s} - {desc}")
        
        if not success and error:
            print(f"   說明: {error}")
        
        results["可選依賴"].append({
            "name": name,
            "description": desc,
            "required": required,
            "success": success,
            "error": error
        })
    
    # 統計結果
    print()
    print("=" * 80)
    print("📊 測試總結")
    print("=" * 80)
    
    required_deps = [r for r in results["必需依賴"] if r["required"]]
    required_passed = sum(1 for r in required_deps if r["success"])
    required_total = len(required_deps)
    
    optional_passed = sum(1 for r in results["可選依賴"] if r["success"])
    optional_total = len(results["可選依賴"])
    
    print(f"\n✅ 必需依賴: {required_passed}/{required_total} 通過")
    print(f"⚠️  可選依賴: {optional_passed}/{optional_total} 通過")
    
    # 列出缺失的必需依賴
    missing_required = [r for r in required_deps if not r["success"]]
    
    if missing_required:
        print()
        print("❌ 缺失的必需依賴:")
        print("-" * 80)
        for dep in missing_required:
            print(f"  • {dep['name']:30s} - {dep['description']}")
            if dep['error']:
                print(f"    錯誤: {dep['error']}")
        
        # 生成安裝命令
        print()
        print("📋 安裝缺失依賴的命令:")
        print("-" * 80)
        
        missing_names = []
        for dep in missing_required:
            # 處理特殊的包名映射
            pkg_name = dep['name']
            if pkg_name == "f5_tts.api":
                continue  # F5-TTS 內部模組
            elif pkg_name == "f5_tts.model":
                continue
            elif pkg_name == "f5_tts.infer.utils_infer":
                continue
            elif pkg_name == "hydra-core":
                missing_names.append("hydra-core")
            elif pkg_name == "rjieba":
                missing_names.append("rjieba")
            elif pkg_name == "x_transformers":
                missing_names.append("x-transformers")
            else:
                missing_names.append(pkg_name)
        
        if missing_names:
            print(f"\npip install {' '.join(missing_names)}")
    
    # 列出缺失的可選依賴
    missing_optional = [r for r in results["可選依賴"] if not r["success"]]
    
    if missing_optional:
        print()
        print("⚠️  缺失的可選依賴（不影響基本使用）:")
        print("-" * 80)
        for dep in missing_optional:
            print(f"  • {dep['name']:30s} - {dep['description']}")
    
    # 最終狀態
    print()
    print("=" * 80)
    
    if required_passed == required_total:
        print("🎉 所有必需依賴已安裝！F5-TTS 可以正常使用。")
        return 0
    else:
        print(f"⚠️  缺少 {required_total - required_passed} 個必需依賴，請安裝後再使用 F5-TTS。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

