"""
Quick Start Script
Automated setup and initialization
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n→ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Quick start setup"""
    print_header("Air Quality System - Quick Start")
    
    print("\nThis script will:")
    print("  1. Check Python installation")
    print("  2. Create virtual environment")
    print("  3. Install dependencies")
    print("  4. Initialize database")
    print("  5. Fetch initial data")
    print("  6. Run verification tests")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Check Python version
    print_header("Step 1: Checking Python")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    else:
        print("✗ Python 3.8 or higher required")
        return False
    
    # Step 2: Create virtual environment
    print_header("Step 2: Creating Virtual Environment")
    if not Path("venv").exists():
        if run_command("python -m venv venv", "Creating virtual environment"):
            print("✓ Virtual environment created")
        else:
            return False
    else:
        print("✓ Virtual environment already exists")
    
    # Step 3: Activate and install dependencies
    print_header("Step 3: Installing Dependencies")
    
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\python -m pip"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/python -m pip"
    
    if run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        print("✓ Pip upgraded")
    
    if run_command(f"{pip_cmd} install -r requirements.txt", "Installing packages"):
        print("✓ Dependencies installed")
    else:
        print("⚠ Some packages may have failed to install")
        print("You can install them manually later")
    
    # Step 4: Configure environment
    print_header("Step 4: Environment Configuration")
    
    if not Path(".env").exists():
        if Path(".env.example").exists():
            # Copy example to .env
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file from template")
            print("\n⚠ IMPORTANT: Edit .env file and add your:")
            print("  - Database credentials")
            print("  - API keys (optional but recommended)")
            input("\nPress Enter after editing .env file...")
        else:
            print("✗ .env.example not found")
            return False
    else:
        print("✓ .env file already exists")
    
    # Step 5: Initialize database
    print_header("Step 5: Database Initialization")
    
    response = input("Do you want to initialize the database now? (y/n): ")
    if response.lower() == 'y':
        if os.name == 'nt':
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        if run_command(f"{python_cmd} scripts/init_database.py", "Initializing database"):
            print("✓ Database initialized")
        else:
            print("⚠ Database initialization failed")
            print("Make sure PostgreSQL is running and credentials are correct")
    else:
        print("⊗ Skipped database initialization")
    
    # Step 6: Fetch initial data
    print_header("Step 6: Fetching Initial Data")
    
    response = input("Do you want to fetch initial air quality data? (y/n): ")
    if response.lower() == 'y':
        if run_command(f"{python_cmd} scripts/fetch_data.py", "Fetching data"):
            print("✓ Initial data fetched")
        else:
            print("⚠ Data fetching failed")
            print("Check your API keys and internet connection")
    else:
        print("⊗ Skipped data fetching")
    
    # Step 7: Run tests
    print_header("Step 7: System Verification")
    
    response = input("Do you want to run verification tests? (y/n): ")
    if response.lower() == 'y':
        run_command(f"{python_cmd} tests/test_system.py", "Running tests")
    
    # Final instructions
    print_header("Setup Complete!")
    
    print("\n✓ Your Air Quality Analysis System is ready!")
    print("\nNext steps:")
    print("\n1. To run the dashboard:")
    if os.name == 'nt':
        print("   venv\\Scripts\\streamlit run app.py")
    else:
        print("   venv/bin/streamlit run app.py")
    
    print("\n2. To fetch latest data:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python scripts/fetch_data.py")
    else:
        print("   venv/bin/python scripts/fetch_data.py")
    
    print("\n3. To generate forecasts:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python scripts/run_forecasting.py")
    else:
        print("   venv/bin/python scripts/run_forecasting.py")
    
    print("\n4. Read documentation:")
    print("   - README.md - Overview")
    print("   - INSTALLATION.md - Detailed installation guide")
    print("   - USAGE_GUIDE.md - How to use the system")
    
    print("\n" + "=" * 60)
    print("  Thank you for using Air Quality Analysis System!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⊗ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)
