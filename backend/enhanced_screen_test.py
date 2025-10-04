"""
Enhanced Live Screen Analysis Test
Captures the entire screen and works with any application
"""

import time
import json
import cv2
import numpy as np
from PIL import Image, ImageGrab
import base64
import io
from ai_screen_reader import AIScreenReader

def capture_full_screen():
    """Capture the entire screen"""
    try:
        screenshot = ImageGrab.grab()

        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot_cv
    except Exception as e:
        print(f"ERROR: Failed to capture screen: {e}")
        return None

def analyze_screen_with_gemini(screen_reader, screenshot_cv):
    """Analyze screenshot with Gemini"""
    try:
        _, buffer = cv2.imencode('.jpg', screenshot_cv)
        screenshot_b64 = base64.b64encode(buffer).decode('utf-8')
        
        explanation = screen_reader.llm_interface.interpret_screen_context(screenshot_b64, "")
        
        return explanation, screenshot_b64
    except Exception as e:
        print(f"ERROR: Gemini analysis failed: {e}")
        return None, None

def main():
    print("AI Screen Reader - Enhanced Live Analysis")
    print("=" * 50)
    print("This will capture your ENTIRE screen and analyze it with Gemini 2.5 Flash")
    print("You can open any application and it will be analyzed!")
    print("=" * 50)
    

    api_key = "AIzaSyAwG3_jcnVEnjmERlNAEWetJLv_bVTL_BA"
    
    try:
        # Initialize the screen reader
        print("\nInitializing AI Screen Reader...")
        screen_reader = AIScreenReader(api_key)
        print("SUCCESS: Screen Reader initialized successfully!")
        
        while True:
            print("\n" + "=" * 50)
            print("Press ENTER to capture and analyze your current screen")
            print("Type 'quit' to exit")
            print("=" * 50)
            
            user_input = input("Command: ").strip().lower()
            
            if user_input == 'quit':
                print("Goodbye!")
                break
            
            print("\nCapturing your entire screen...")
            
            # Capture full screen
            screenshot = capture_full_screen()
            if screenshot is None:
                print("ERROR: Failed to capture screen")
                continue
            
            print("SUCCESS: Screen captured!")
            print("Analyzing with Gemini 2.5 Flash...")
            
            # Analyze with Gemini
            explanation, screenshot_b64 = analyze_screen_with_gemini(screen_reader, screenshot)
            
            if explanation is None:
                print("ERROR: Analysis failed")
                continue
            
            # Display results
            print("\n" + "=" * 50)
            print("LIVE SCREEN ANALYSIS RESULTS:")
            print("=" * 50)
            
            print(f"Application: {explanation.get('application_name', 'Unknown')}")
            print(f"Screen Type: {explanation.get('screen_type', 'Unknown')}")
            print(f"Current Context: {explanation.get('current_context', 'Not specified')}")
            print(f"User Workflow: {explanation.get('user_workflow', 'Not specified')}")
            print(f"Next Steps: {explanation.get('next_steps', 'Not specified')}")
            print(f"Confidence: {explanation.get('confidence', 0):.2f}")
            
            # Visible elements
            visible_elements = explanation.get('visible_elements', [])
            if visible_elements:
                print(f"\nVISIBLE ELEMENTS:")
                for i, element in enumerate(visible_elements[:5], 1):
                    print(f"   {i}. {element.get('element', 'Unknown')}: {element.get('content', 'No content')}")
                    print(f"      Purpose: {element.get('purpose', 'Not specified')}")
                    print(f"      Importance: {element.get('importance', 'medium')}")
            
            # Important data
            important_data = explanation.get('important_data')
            if important_data:
                print(f"\nIMPORTANT DATA:")
                print(f"   {important_data}")
            
            print(f"\nSUCCESS: Analysis completed!")
            print("You can now open any other application and press ENTER to analyze it!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()