import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from core.logger import logger
from core.device_manager import device_manager

class OCRInpaintProcessor:
    """
    OCR-based subtitle detection and inpainting processor.
    Uses EasyOCR for text detection and OpenCV/Lama for inpainting.
    """
    def __init__(self, use_gpu=True):
        self.ocr_model = None
        self.use_gpu = use_gpu and device_manager.get_device() in ['cuda', 'mps']
        logger.info("OCRInpaintProcessor initialized (Lazy Loading).")

    def load_models(self):
        """
        Load OCR model. Inpainting uses OpenCV built-in methods.
        """
        if self.ocr_model is not None:
            logger.info("OCR model already loaded.")
            return
        
        try:
            import easyocr
            logger.info("Loading EasyOCR model...")
            
            # EasyOCR supports multiple languages
            # Use ['en', 'ch_sim'] for English and Simplified Chinese
            # Use ['en', 'ch_tra'] for English and Traditional Chinese
            # Adjust based on your needs
            self.ocr_model = easyocr.Reader(
                ['en', 'ch_sim', 'ch_tra', 'ja', 'ko'],  # Multi-language support
                gpu=self.use_gpu
            )
            logger.info("✅ EasyOCR model loaded successfully")
            
        except ImportError as e:
            logger.error(f"EasyOCR not installed: {e}")
            logger.warning("Falling back to pass-through mode (no subtitle removal)")
            self.ocr_model = None
        except Exception as e:
            logger.error(f"Failed to load OCR model: {e}")
            logger.warning("Falling back to pass-through mode")
            self.ocr_model = None

    def detect_text_regions(self, frame, min_confidence=0.3):
        """
        Detect text regions in a frame using OCR.
        
        Args:
            frame: Input frame (BGR image)
            min_confidence: Minimum confidence threshold for text detection
            
        Returns:
            List of bounding boxes [[x1, y1, x2, y2], ...]
        """
        if self.ocr_model is None:
            return []
        
        try:
            # EasyOCR expects RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect text
            results = self.ocr_model.readtext(frame_rgb)
            
            # Extract bounding boxes with confidence filtering
            boxes = []
            for (bbox, text, confidence) in results:
                if confidence >= min_confidence:
                    # Convert bbox format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                    # to [x1, y1, x2, y2]
                    x_coords = [pt[0] for pt in bbox]
                    y_coords = [pt[1] for pt in bbox]
                    x1, y1 = int(min(x_coords)), int(min(y_coords))
                    x2, y2 = int(max(x_coords)), int(max(y_coords))
                    boxes.append([x1, y1, x2, y2])
            
            return boxes
            
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return []

    def create_inpaint_mask(self, frame_shape, boxes, padding=5):
        """
        Create inpainting mask from text bounding boxes.
        
        Args:
            frame_shape: Shape of the frame (height, width, channels)
            boxes: List of bounding boxes [[x1, y1, x2, y2], ...]
            padding: Padding around text boxes (pixels)
            
        Returns:
            Binary mask for inpainting
        """
        height, width = frame_shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        for box in boxes:
            x1, y1, x2, y2 = box
            # Add padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(width, x2 + padding)
            y2 = min(height, y2 + padding)
            # Draw white rectangle on mask
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        return mask

    def inpaint_frame(self, frame, mask):
        """
        Inpaint frame using OpenCV.
        
        Args:
            frame: Input frame
            mask: Binary mask (white = areas to inpaint)
            
        Returns:
            Inpainted frame
        """
        if mask.sum() == 0:
            # No text detected, return original
            return frame
        
        try:
            # Use Telea algorithm (fast) or NS algorithm (slower but better quality)
            # INPAINT_TELEA is faster, INPAINT_NS is better quality
            inpainted = cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
            return inpainted
        except Exception as e:
            logger.error(f"Inpainting failed: {e}")
            return frame
    
    def process_video(self, video_path, output_path, detect_every_n_frames=5, min_confidence=0.4):
        """
        Process video to remove subtitles using OCR and inpainting.
        
        Args:
            video_path: Path to input video
            output_path: Path to output video
            detect_every_n_frames: Run OCR every N frames (for performance)
            min_confidence: Minimum OCR confidence threshold
            
        Returns:
            Path to output video
        """
        logger.info(f"Processing OCR & Inpaint for {video_path}...")
        
        # Load models
        if self.ocr_model is None:
            self.load_models()
        
        # If OCR not available, fall back to pass-through
        if self.ocr_model is None:
            logger.warning("OCR not available. Copying video without subtitle removal.")
            return self._passthrough_video(video_path, output_path)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video {video_path}")
            return None
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create output video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        logger.info(f"Video: {width}x{height} @ {fps:.2f}fps, {total_frames} frames")
        logger.info(f"OCR detection every {detect_every_n_frames} frames")
        
        frame_count = 0
        last_boxes = []  # Cache last detected boxes
        text_frames_detected = 0
        
        with tqdm(total=total_frames, desc="Processing frames") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect text every N frames
                if frame_count % detect_every_n_frames == 0:
                    boxes = self.detect_text_regions(frame, min_confidence=min_confidence)
                    if boxes:
                        last_boxes = boxes
                        text_frames_detected += 1
                
                # Inpaint if text detected
                if last_boxes:
                    mask = self.create_inpaint_mask(frame.shape, last_boxes, padding=5)
                    frame = self.inpaint_frame(frame, mask)
                
                out.write(frame)
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        out.release()
        
        logger.info(f"✅ OCR/Inpaint complete. Saved to {output_path}")
        logger.info(f"   Text detected in {text_frames_detected} sample frames")
        
        return output_path

    def _passthrough_video(self, video_path, output_path):
        """
        Copy video without processing (fallback when OCR not available).
        """
        logger.info("Copying video without processing...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        with tqdm(total=total_frames, desc="Copying frames") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                pbar.update(1)
        
        cap.release()
        out.release()
        
        logger.info(f"Video copied to {output_path}")
        return output_path

    def unload(self):
        """
        Unload models and clear memory.
        """
        if self.ocr_model is not None:
            logger.info("Unloading OCR model...")
            del self.ocr_model
            self.ocr_model = None
        device_manager.clear_cache()
        logger.info("OCR memory cleared.")
