"""
Auto Screen Analysis - Captures screen automatically without user input
"""

import os
import sys
import time
import json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from ai_screen_reader import AIScreenReader

def load_api_key():
    """Load API key from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"\'')
                        if api_key:
                            print(f"Loaded API key from .env file")
                            return api_key
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    print("API key not found in .env file!")
    sys.exit(1)

def main():
    print("Auto Screen Analysis")
    print("=" * 50)
    
    api_key = load_api_key()
    
    print("\nInitializing AI Screen Reader...")
    try:
        reader = AIScreenReader(llm_api_key=api_key)
        print("AI Screen Reader initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize AI Screen Reader: {e}")
        return
    
    print("\nCapturing desktop screen automatically...")
    print("This will capture your ENTIRE desktop screen")
    
    try:
        result = reader.analyze_current_screen()
        
        if result.get('success', True): 
            print("\nScreen captured successfully!")
            

            print("\n" + "="*60)
            print("DESKTOP SCREEN ANALYSIS RESULTS")
            print("="*60)
            
            if 'summary' in result and result['summary']:
                print(f"\nSummary: {result['summary']}")

            if 'detailed_analysis' in result and result['detailed_analysis']:
                print(f"\nDetailed Analysis:")
                print(f"{result['detailed_analysis']}")
            
            if 'elements' in result and result['elements']:
                print(f"\nDetected Elements:")
                for element in result['elements']:
                    print(f"  • {element}")
            
            if 'commands' in result and result['commands']:
                print(f"\nSuggested Actions:")
                for action in result['commands']:
                    print(f"  • {action}")
            
            if 'interpretation' in result and 'confidence' in result['interpretation']:
                print(f"\nConfidence Score: {result['interpretation']['confidence']:.1f}%")
            

            print(f"\nAnalysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            print(f"Screen analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
