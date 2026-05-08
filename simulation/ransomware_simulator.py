
import os
import time
import random
import shutil
from pathlib import Path
from datetime import datetime

class RansomwareSimulator:
    """Simulate ransomware behavior for testing"""
    
    def __init__(self, target_dir: str = None):
        if target_dir is None:
            target_dir = os.path.expanduser("~/arcs_monitor/test_files")
        
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        print(f"🎯 Target directory: {self.target_dir}")
    
    def create_test_files(self, count: int = 50):
        """Create test files to encrypt"""
        print(f"📝 Creating {count} test files...")
        
        for i in range(count):
            file_path = self.target_dir / f"document_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(f"Test document {i}\n" * 100)
        
        print(f"✅ Created {count} test files")
    
    def simulate_encryption(self, delay: float = 0.1):
        """Simulate file encryption behavior"""
        print("\n🦠 Starting ransomware simulation...")
        print("⚠️ This will rapidly modify files to trigger detection\n")
        
        files = list(self.target_dir.glob("*.txt"))
        
        if not files:
            print("❌ No files found. Creating test files first...")
            self.create_test_files()
            files = list(self.target_dir.glob("*.txt"))
        
        encrypted_count = 0
        
        for file_path in files:
            try:
                # Read original content
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Simulate encryption (reverse content)
                encrypted_content = content[::-1]
                
                # Write encrypted content
                with open(file_path, 'w') as f:
                    f.write(encrypted_content)
                
                # Rename with suspicious extension
                new_path = file_path.with_suffix('.encrypted')
                # Remove existing encrypted file if it exists
                if new_path.exists():
                    new_path.unlink()
                file_path.rename(new_path)
                
                encrypted_count += 1
                print(f"🔒 Encrypted: {file_path.name} -> {new_path.name}")
                
                time.sleep(delay)
            
            except Exception as e:
                print(f"❌ Error encrypting {file_path}: {e}")
        
        print(f"\n✅ Simulation complete: {encrypted_count} files encrypted")
        print("🚨 This should trigger HIGH risk alerts in the system!")
    
    def simulate_rapid_modifications(self, iterations: int = 30):
        """Simulate rapid file modifications"""
        print("\n🦠 Simulating rapid file modifications...")
        
        test_file = self.target_dir / "rapid_test.txt"
        test_file.write_text("Initial content")
        
        for i in range(iterations):
            with open(test_file, 'a') as f:
                f.write(f"\nModification {i} at {datetime.now()}")
            time.sleep(0.1)
        
        print(f"✅ Performed {iterations} rapid modifications")
    
    def simulate_mass_deletion(self):
        """Simulate mass file deletion"""
        print("\n🦠 Simulating mass file deletion...")
        
        files = list(self.target_dir.glob("*.txt"))
        deleted = 0
        
        for file_path in files[:10]:  # Delete first 10 files
            try:
                file_path.unlink()
                deleted += 1
                print(f"🗑️ Deleted: {file_path.name}")
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}")
        
        print(f"✅ Deleted {deleted} files")
    
    def cleanup(self):
        """Clean up test files"""
        print("\n🧹 Cleaning up test files...")
        
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir)
            print("✅ Cleanup complete")
    
    def run_full_simulation(self):
        """Run complete ransomware simulation"""
        print("=" * 60)
        print("🦠 RANSOMWARE SIMULATION")
        print("=" * 60)
        
        # Create test files
        self.create_test_files(count=30)
        
        print("\n⏳ Waiting 5 seconds before starting attack...")
        time.sleep(5)
        
        # Simulate rapid modifications
        self.simulate_rapid_modifications(iterations=25)
        
        time.sleep(2)
        
        # Simulate encryption
        self.simulate_encryption(delay=0.05)
        
        print("\n" + "=" * 60)
        print("✅ SIMULATION COMPLETE")
        print("=" * 60)
        print("\nCheck the ARCS dashboard for alerts!")
        print("Expected: HIGH risk alerts with automated containment")

def main():
    simulator = RansomwareSimulator()
    
    print("\n🎮 Ransomware Simulator")
    print("1. Run full simulation")
    print("2. Create test files only")
    print("3. Simulate encryption only")
    print("4. Simulate rapid modifications")
    print("5. Cleanup test files")
    print("6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == "1":
        simulator.run_full_simulation()
    elif choice == "2":
        simulator.create_test_files()
    elif choice == "3":
        simulator.simulate_encryption()
    elif choice == "4":
        simulator.simulate_rapid_modifications()
    elif choice == "5":
        simulator.cleanup()
    elif choice == "6":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
