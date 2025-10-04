#!/usr/bin/env python3
"""
Simple Live Screen Analysis Test
Works without Tesseract OCR - uses only Gemini 2.5 Flash
"""

import time
import json
from ai_screen_reader import AIScreenReader

def main():
    print("AI Screen Reader - Simple Live Analysis (No OCR Required)")
    print("=" * 60)
    
    # Get API key from user
    api_key = input("Enter your Google API key (starts with AIza...): ").strip()
    
    if not api_key or not api_key.startswith('AIza'):
        print("ERROR: Invalid API key format. Please enter a valid Google API key.")
        return
    
    try:
        # Initialize the screen reader
        print("\nInitializing AI Screen Reader...")
        screen_reader = AIScreenReader(api_key)
        print("SUCCESS: Screen Reader initialized successfully!")
        
        print("\nAnalyzing current screen with Gemini 2.5 Flash...")
        print("   (OCR is optional - Gemini will analyze the image directly)")
        
        # Analyze the current screen
        result = screen_reader.analyze_current_screen()
        
        if "error" in result:
            print(f"ERROR: {result['error']}")
            return
        
        # Display the analysis
        print("\nLIVE SCREEN ANALYSIS RESULTS:")
        print("-" * 40)
        
        # Summary
        summary = result.get('summary', {})
        print(f"Application: {summary.get('application', 'Unknown')}")
        print(f"Screen Type: {summary.get('screen_type', 'Unknown')}")
        print(f"Context: {summary.get('context', 'Screen analysis')}")
        print(f"Elements Found: {summary.get('elements_found', 0)}")
        print(f"Commands Generated: {summary.get('commands_generated', 0)}")
        print(f"Confidence: {summary.get('confidence', 0):.2f}")
        
        # Detailed interpretation
        interpretation = result.get('interpretation', {})
        if interpretation:
            print(f"\nDETAILED EXPLANATION:")
            print(f"   Application: {interpretation.get('application_name', 'Unknown')}")
            print(f"   Current Context: {interpretation.get('current_context', 'Not specified')}")
            print(f"   User Workflow: {interpretation.get('user_workflow', 'Not specified')}")
            print(f"   Next Steps: {interpretation.get('next_steps', 'Not specified')}")
            
            # Visible elements
            visible_elements = interpretation.get('visible_elements', [])
            if visible_elements:
                print(f"\nVISIBLE ELEMENTS:")
                for i, element in enumerate(visible_elements[:5], 1):  # Show first 5
                    print(f"   {i}. {element.get('element', 'Unknown')}: {element.get('content', 'No content')}")
                    print(f"      Purpose: {element.get('purpose', 'Not specified')}")
                    print(f"      Importance: {element.get('importance', 'medium')}")
            
            # Important data
            important_data = interpretation.get('important_data')
            if important_data:
                print(f"\nIMPORTANT DATA:")
                print(f"   {important_data}")
        
        # Commands
        commands = result.get('commands', [])
        if commands:
            print(f"\nSUGGESTED ACTIONS:")
            for i, cmd in enumerate(commands, 1):
                print(f"   {i}. {cmd['action_type'].upper()}: {cmd['target']}")
                if cmd.get('coordinates'):
                    print(f"      Coordinates: {cmd['coordinates']}")
                print(f"      Confidence: {cmd['confidence']:.2f}")
        
        print(f"\nSUCCESS: Live screen analysis completed!")
        print(f"INFO: This analysis was done using only Gemini 2.5 Flash vision capabilities!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
