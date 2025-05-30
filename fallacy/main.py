import os
import subprocess

def run_fallacy_scripts():
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.startswith("fallacy_") and filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                print(f"Running: {file_path}")
                try:
                    subprocess.run(["python", file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error while running {file_path}: {e}")

if __name__ == "__main__":
    run_fallacy_scripts()
