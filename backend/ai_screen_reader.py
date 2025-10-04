import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import base64
import json
import time
import threading
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenRegion(Enum):
    FULL_SCREEN = "full_screen"
    WINDOW = "window"
    CUSTOM = "custom"

@dataclass
class ScreenElement:
    """Represents a UI element detected on screen"""
    text: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    element_type: str  # button, text, input, etc.
    coordinates: Tuple[int, int]  # center point

@dataclass
class ActionCommand:
    """Represents an actionable command generated from screen analysis"""
    action_type: str  # click, type, scroll, etc.
    target: str  # description of target element
    coordinates: Optional[Tuple[int, int]]
    parameters: Dict[str, any]
    confidence: float

class ScreenCapture:
    """Handles screen capture and preprocessing"""
    
    def __init__(self):
        self.capture_region = ScreenRegion.FULL_SCREEN
        self.custom_region = None
        
    def capture_screen(self, region: ScreenRegion = ScreenRegion.FULL_SCREEN) -> np.ndarray:
        """Capture screen or specific region"""
        try:
            if region == ScreenRegion.FULL_SCREEN:
                screenshot = ImageGrab.grab()
            elif region == ScreenRegion.WINDOW:
                # For demo purposes, capture full screen
                # In production, you'd implement window-specific capture
                screenshot = ImageGrab.grab()
            else:
                # Custom region capture
                if self.custom_region:
                    screenshot = ImageGrab.grab(bbox=self.custom_region)
                else:
                    screenshot = ImageGrab.grab()
            
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot_cv
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        

        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned

class OCRProcessor:
    """Handles OCR processing and text extraction"""
    
    def __init__(self):

        pass
    
    def extract_text_with_boxes(self, image: np.ndarray) -> List[Dict]:
        """Extract text with bounding boxes using Tesseract (optional)"""
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            elements = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                confidence = int(data['conf'][i])
                
                if confidence > 30 and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    element = {
                        'text': text,
                        'bbox': (x, y, w, h),
                        'confidence': confidence / 100.0,
                        'coordinates': (x + w//2, y + h//2)
                    }
                    elements.append(element)
            
            return elements
        except Exception as e:
            logger.warning(f"OCR processing failed (Tesseract not available): {e}")
            return []
    
    def extract_text_simple(self, image: np.ndarray) -> str:
        """Simple text extraction without bounding boxes"""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"Simple OCR failed (Tesseract not available): {e}")
            return ""

class LLMInterface:
    """Interface for Gemini 2.5 Flash integration and command generation"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)
    
    def analyze_screen_elements(self, elements: List[Dict], screenshot_b64: str) -> List[ActionCommand]:
        """Use Gemini 2.5 Flash to analyze screen elements and generate actionable commands"""
        try:
            # Convert base64 image to PIL Image for Gemini
            image_data = base64.b64decode(screenshot_b64)
            image = Image.open(io.BytesIO(image_data))
            
            prompt = f"""
            You are an AI assistant analyzing a live screen capture. Please provide a detailed analysis of what you see on this screen.
            
            Analyze the screenshot and provide:
            1. A comprehensive description of what's currently displayed
            2. Identify all UI elements (buttons, text fields, menus, images, etc.)
            3. Explain the purpose and context of each element
            4. Suggest what actions a user might want to perform
            5. Generate specific, actionable commands
            
            Format your response as JSON with this structure:
            {{
                "screen_description": "Detailed description of what's on the screen",
                "ui_elements": [
                    {{
                        "element_type": "button/text/input/image/menu/etc",
                        "description": "What this element is and does",
                        "location": "Where it's positioned",
                        "purpose": "Why it exists on this screen"
                    }}
                ],
                "context": "Overall context and purpose of this screen",
                "suggested_actions": [
                    {{
                        "action_type": "click/type/scroll/navigate/etc",
                        "target": "What to interact with",
                        "coordinates": [x, y],
                        "parameters": {{"additional_info": "value"}},
                        "confidence": 0.85,
                        "explanation": "Why this action makes sense"
                    }}
                ],
                "screen_type": "login_page/dashboard/form/etc",
                "confidence": 0.90
            }}
            
            Be very detailed and specific in your analysis. Focus on understanding the user's current context and what they might want to accomplish.
            """
            
            # Use Gemini 2.5 Flash for multimodal analysis
            response = self.model_instance.generate_content([prompt, image])
            
            # Parse the JSON response
            try:
                # Clean the response text (remove markdown formatting if present)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                analysis_data = json.loads(response_text)
                
                # Convert to ActionCommand objects
                commands = []
                for action_data in analysis_data.get('suggested_actions', []):
                    command = ActionCommand(
                        action_type=action_data.get('action_type', 'unknown'),
                        target=action_data.get('target', 'Unknown target'),
                        coordinates=tuple(action_data.get('coordinates', [0, 0])) if action_data.get('coordinates') else None,
                        parameters=action_data.get('parameters', {}),
                        confidence=action_data.get('confidence', 0.5)
                    )
                    commands.append(command)
                
                # Store the detailed analysis for later use
                self.last_analysis = analysis_data
                
                return commands
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini response as JSON: {e}")
                logger.warning(f"Response text: {response.text[:200]}...")
                return self._get_fallback_commands()
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._get_fallback_commands()
    
    def _get_fallback_commands(self) -> List[ActionCommand]:
        """Fallback commands when Gemini API fails"""
        return [
            ActionCommand(
                action_type="click",
                target="Primary action button",
                coordinates=(400, 300),
                parameters={"button_text": "Action"},
                confidence=0.75
            ),
            ActionCommand(
                action_type="type",
                target="Input field",
                coordinates=(300, 200),
                parameters={"text": "input", "field_type": "text"},
                confidence=0.70
            ),
            ActionCommand(
                action_type="scroll",
                target="Page content",
                coordinates=None,
                parameters={"direction": "down", "amount": 3},
                confidence=0.65
            )
        ]
    
    def interpret_screen_context(self, screenshot_b64: str, user_intent: str = "") -> Dict:
        """Use Gemini 2.5 Flash to understand screen context and provide detailed explanations"""
        try:
            # Convert base64 image to PIL Image for Gemini
            image_data = base64.b64decode(screenshot_b64)
            image = Image.open(io.BytesIO(image_data))
            
            prompt = f"""
            You are an expert UI/UX analyst. Analyze this live screen capture and provide a comprehensive explanation of what the user is seeing and what they can do.
            
            User Intent: {user_intent if user_intent else "General screen analysis"}
            
            Please provide a detailed analysis including:
            1. What application/website this appears to be
            2. What the user is currently doing or looking at
            3. All visible UI elements and their purposes
            4. The user's current workflow context
            5. What the user might want to do next
            6. Any important information or data visible on screen
            
            Format as JSON:
            {{
                "application_name": "Name of the app/website",
                "current_context": "What the user is currently doing",
                "screen_type": "login_page/dashboard/form/settings/etc",
                "visible_elements": [
                    {{
                        "element": "Button/Text/Input/Image/etc",
                        "content": "What it says or shows",
                        "purpose": "Why it's there",
                        "importance": "high/medium/low"
                    }}
                ],
                "user_workflow": "What the user is trying to accomplish",
                "next_steps": "What the user might want to do next",
                "important_data": "Any key information visible",
                "accessibility_notes": "Any accessibility considerations",
                "confidence": 0.95
            }}
            
            Be thorough and helpful. Think like you're explaining the screen to someone who can't see it.
            """
            
            response = self.model_instance.generate_content([prompt, image])
            
            # Parse the JSON response
            try:
                # Clean the response text (remove markdown formatting if present)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                interpretation = json.loads(response_text)
                return interpretation
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini context response as JSON: {e}")
                logger.warning(f"Response text: {response.text[:200]}...")
                return self._get_fallback_interpretation()
            
        except Exception as e:
            logger.error(f"Gemini screen interpretation failed: {e}")
            return self._get_fallback_interpretation()
    
    def _get_fallback_interpretation(self) -> Dict:
        """Fallback interpretation when Gemini API fails"""
        return {
            "screen_type": "unknown",
            "primary_elements": ["text_elements", "interactive_elements"],
            "suggested_actions": ["click_element", "type_text"],
            "context": "Screen analysis completed with basic OCR detection",
            "confidence": 0.60
        }
    
    def get_detailed_analysis(self) -> Dict:
        """Get the last detailed analysis from Gemini"""
        return getattr(self, 'last_analysis', {})

class AIScreenReader:
    """Main class that orchestrates the AI Screen Reader functionality"""
    
    def __init__(self, llm_api_key: str):
        self.screen_capture = ScreenCapture()
        self.ocr_processor = OCRProcessor()
        self.llm_interface = LLMInterface(llm_api_key)
        self.is_running = False
        self.capture_thread = None
    
    def start_monitoring(self, interval: float = 2.0):
        """Start continuous screen monitoring"""
        self.is_running = True
        self.capture_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.capture_thread.start()
        logger.info("Screen monitoring started")
    
    def stop_monitoring(self):
        """Stop screen monitoring"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join()
        logger.info("Screen monitoring stopped")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Capture screen
                screenshot = self.screen_capture.capture_screen()
                if screenshot is None:
                    time.sleep(interval)
                    continue
                
                # Process with OCR
                processed_image = self.screen_capture.preprocess_image(screenshot)
                elements = self.ocr_processor.extract_text_with_boxes(processed_image)
                
                # Convert screenshot to base64 for LLM
                _, buffer = cv2.imencode('.jpg', screenshot)
                screenshot_b64 = base64.b64encode(buffer).decode('utf-8')
                
                # Generate commands
                commands = self.llm_interface.analyze_screen_elements(elements, screenshot_b64)
                
                # Log results
                logger.info(f"Detected {len(elements)} elements, generated {len(commands)} commands")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)
    
    def analyze_current_screen(self) -> Dict:
        """Analyze current screen and return comprehensive results with detailed explanations"""
        try:
            # Capture and process
            screenshot = self.screen_capture.capture_screen()
            if screenshot is None:
                return {"error": "Failed to capture screen"}
            
            processed_image = self.screen_capture.preprocess_image(screenshot)
            elements = self.ocr_processor.extract_text_with_boxes(processed_image)
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', screenshot)
            screenshot_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # LLM analysis with detailed explanations
            commands = self.llm_interface.analyze_screen_elements(elements, screenshot_b64)
            interpretation = self.llm_interface.interpret_screen_context(screenshot_b64, "")
            detailed_analysis = self.llm_interface.get_detailed_analysis()
            
            return {
                "timestamp": time.time(),
                "elements": elements,
                "commands": [
                    {
                        "action_type": cmd.action_type,
                        "target": cmd.target,
                        "coordinates": cmd.coordinates,
                        "parameters": cmd.parameters,
                        "confidence": cmd.confidence
                    } for cmd in commands
                ],
                "interpretation": interpretation,
                "detailed_analysis": detailed_analysis,
                "screenshot_b64": screenshot_b64,
                "summary": {
                    "screen_type": interpretation.get('screen_type', 'unknown'),
                    "application": interpretation.get('application_name', 'Unknown'),
                    "context": interpretation.get('current_context', 'Screen analysis'),
                    "elements_found": len(elements),
                    "commands_generated": len(commands),
                    "confidence": interpretation.get('confidence', 0.5)
                }
            }
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Initialize with Google API key (you'll need to set this)
    api_key = "your-google-api-key-here"
    screen_reader = AIScreenReader(api_key)
    
    # Analyze current screen
    result = screen_reader.analyze_current_screen()
    print("Screen Analysis Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Start monitoring (uncomment to test)
    # screen_reader.start_monitoring(interval=5.0)
    # time.sleep(30)  # Monitor for 30 seconds
    # screen_reader.stop_monitoring()
