import os
import shutil
import glob

def cleanup():
    print("--- [SUBIT-T Release Cleanup] ---")
    
    # 1. Clear evaluation datasets (Large files)
    eval_files = glob.glob("eval/synthetic_*.jsonl")
    for f in eval_files:
        try:
            os.remove(f)
            print(f"Removed: {f}")
        except Exception as e:
            print(f"Error removing {f}: {e}")
            
    # 2. Clear build artifacts
    dirs_to_remove = ["build", "dist", "*.egg-info", "**/__pycache__"]
    for pattern in dirs_to_remove:
        for d in glob.glob(pattern, recursive=True):
            if os.path.isdir(d):
                try:
                    shutil.rmtree(d)
                    print(f"Removed directory: {d}")
                except Exception as e:
                    print(f"Error removing directory {d}: {e}")
                    
    print("\nCleanup complete. Repository is now in 'v0.4.0' clean state.")

if __name__ == "__main__":
    cleanup()
