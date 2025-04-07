#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def build_standalone_exe():
    """Build a single, standalone executable that can be distributed as-is."""
    print("=== Schedule 1 Strain Renamer - Simple EXE Builder ===")
    print("Building standalone executable...\n")
    
    # Check for PyInstaller
    try:
        import PyInstaller
        print("PyInstaller detected.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.\n")
        except Exception as e:
            print(f"Failed to install PyInstaller: {e}")
            print("Please install it manually with: pip install pyinstaller")
            return False
    
    # Determine the executable name based on platform
    exe_name = "Schedule1StrainRenamer"
    if platform.system() == "Windows":
        exe_name += ".exe"
    
    # Create a simple PyInstaller command
    cmd = [
        "pyinstaller",
        f"--name={exe_name}",
        "--onefile",  # This creates a single standalone EXE
        "--windowed",  # No console window
        "schedule1_rename_tool.py"
    ]
    
    # Run PyInstaller
    try:
        subprocess.check_call(cmd)
        exe_path = os.path.join("dist", exe_name)
        
        if os.path.exists(exe_path):
            print("\n✓ Success! Standalone executable created successfully.")
            print(f"\nYour executable is located at: {os.path.abspath(exe_path)}")
            
            if platform.system() == "Windows":
                print("\nYou can now distribute this single EXE file to your users.")
                print("They can simply double-click it to run the application - no installation required.")
            else:
                print("\nThis executable was built on Linux/Mac and will work on this platform.")
                print("To build a Windows .exe file, you need to run this script on Windows.")
                print("\nFor Windows users, you should:")
                print("1. Copy this project to a Windows machine")
                print("2. Run this same script on Windows")
                print("3. Distribute the resulting .exe file")
            
            return True
        else:
            print("\nError: Executable was not created.")
            return False
    except Exception as e:
        print(f"\nError building executable: {e}")
        return False

if __name__ == "__main__":
    build_standalone_exe() 