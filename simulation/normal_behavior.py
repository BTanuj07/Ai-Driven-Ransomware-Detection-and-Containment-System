import os
import time
import random
from pathlib import Path
from datetime import datetime

class NormalBehaviorSimulator:
    """Simulate normal user behavior for baseline"""
    
    def __init__(self, target_dir: str = None):
        if target_dir is None:
            target_dir = os.path.expanduser("~/arcs_monitor/normal_files")
        
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Working directory: {self.target_dir}")
    
    def simulate_document_editing(self, duration: int = 60):
        """Simulate normal document editing"""
        print(f"\n📝 Simulating normal document editing for {duration} seconds...")
        
        doc_file = self.target_dir / "work_document.txt"
        doc_file.write_text("Work document\n")
        
        start_time = time.time()
        edit_count = 0
        
        while time.time() - start_time < duration:
            # Simulate occasional edits (2-5 per minute)
            with open(doc_file, 'a') as f:
                f.write(f"Edit at {datetime.now()}: {random.choice(['Meeting notes', 'Task update', 'Project info'])}\n")
            
            edit_count += 1
            print(f"✏️ Edit #{edit_count}")
            
            # Random delay between edits (10-30 seconds)
            time.sleep(random.uniform(10, 30))
        
        print(f"✅ Completed {edit_count} normal edits")
    
    def simulate_file_operations(self, count: int = 10):
        """Simulate normal file operations"""
        print(f"\n📂 Simulating {count} normal file operations...")
        
        for i in range(count):
            # Create file
            file_path = self.target_dir / f"file_{i}.txt"
            file_path.write_text(f"Normal file {i}\n")
            print(f"✅ Created: {file_path.name}")
            
            time.sleep(random.uniform(2, 5))
            
            # Modify file
            with open(file_path, 'a') as f:
                f.write("Additional content\n")
            print(f"✏️ Modified: {file_path.name}")
            
            time.sleep(random.uniform(2, 5))
        
        print(f"✅ Completed {count} file operations")
    
    def simulate_browsing(self, duration: int = 30):
        """Simulate web browsing activity"""
        print(f"\n🌐 Simulating browsing activity for {duration} seconds...")
        
        start_time = time.time()
        page_count = 0
        
        while time.time() - start_time < duration:
            # Simulate page view
            page_count += 1
            print(f"🌐 Page view #{page_count}")
            
            # Random delay between pages (3-8 seconds)
            time.sleep(random.uniform(3, 8))
        
        print(f"✅ Simulated {page_count} page views")
    
    def run_normal_session(self, duration: int = 120):
        """Run a normal work session"""
        print("=" * 60)
        print("👤 NORMAL BEHAVIOR SIMULATION")
        print("=" * 60)
        
        print(f"\n⏱️ Running {duration} second session...")
        
        # Mix of activities
        self.simulate_file_operations(count=5)
        time.sleep(5)
        self.simulate_document_editing(duration=30)
        time.sleep(5)
        self.simulate_browsing(duration=20)
        
        print("\n" + "=" * 60)
        print("✅ NORMAL SESSION COMPLETE")
        print("=" * 60)
        print("\nThis should NOT trigger alerts (or only LOW risk)")

def main():
    simulator = NormalBehaviorSimulator()
    
    print("\n👤 Normal Behavior Simulator")
    print("1. Run normal session (2 minutes)")
    print("2. Simulate document editing")
    print("3. Simulate file operations")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        simulator.run_normal_session()
    elif choice == "2":
        simulator.simulate_document_editing(duration=60)
    elif choice == "3":
        simulator.simulate_file_operations(count=10)
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
