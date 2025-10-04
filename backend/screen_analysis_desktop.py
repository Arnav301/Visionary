#!/usr/bin/env python3
"""
Desktop Screen Analysis - Captures screen without terminal interference
"""

import os
import sys
import time
import json
from datetime import datetime
import subprocess

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from ai_screen_reader import AIScreenReader

def load_api_key():
    """Load API key from .env file or prompt user"""
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
    

    api_key = input("Enter your Google API Key (Gemini): ").strip()
    if not api_key:
        print("API key is required!")
        sys.exit(1)
    
    return api_key

def main():
    print("Desktop Screen Analysis")
    print("=" * 50)
    

    api_key = load_api_key()
    

    print("\nInitializing AI Screen Reader...")
    try:
        reader = AIScreenReader(llm_api_key=api_key)
        print("AI Screen Reader initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize AI Screen Reader: {e}")
        return
    
    print("\nThis will capture your ENTIRE desktop screen")
    print("Tip: Open any application you want to analyze")
    print("The AI will provide detailed analysis of what's on your screen")
    print("\nIMPORTANT: This will capture your entire desktop, not just the terminal")
    
    input("\nPress Enter to start screen analysis...")
    
    try:
        print("\nCapturing desktop screen...")

        result = reader.analyze_current_screen()
        
        if result.get('success', True): 
            print("\nScreen captured successfully!")
            
            # Display results
            print("\n" + "="*60)
            print("DESKTOP SCREEN ANALYSIS RESULTS")
            print("="*60)
            
            # Summary
            if 'summary' in result and result['summary']:
                print(f"\nSummary: {result['summary']}")
            
            # Detailed Analysis
            if 'detailed_analysis' in result and result['detailed_analysis']:
                print(f"\nDetailed Analysis:")
                print(f"{result['detailed_analysis']}")
            
            # Screen Elements
            if 'elements' in result and result['elements']:
                print(f"\nDetected Elements:")
                for element in result['elements']:
                    print(f"  • {element}")
            
            # Suggested Actions
            if 'commands' in result and result['commands']:
                print(f"\nSuggested Actions:")
                for action in result['commands']:
                    print(f"  • {action}")
            
            # Confidence Score
            if 'interpretation' in result and 'confidence' in result['interpretation']:
                print(f"\nConfidence Score: {result['interpretation']['confidence']:.1f}%")
            
            # Timestamp
            print(f"\nAnalysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            print(f"Screen analysis failed: {result.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n\nAnalysis stopped by user")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
