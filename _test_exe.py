import subprocess, time, os, sys

exe_path = os.path.join("dist", "StudyDeskPro.exe")
print(f"Launching: {exe_path}")
try:
    proc = subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path) or ".")
    print(f"Process started, PID: {proc.pid}")
    time.sleep(4)
    if proc.poll() is None:
        print("EXE is running (process alive after 4 seconds) - SUCCESS")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Process terminated cleanly")
    else:
        print(f"EXE exited early with code: {proc.returncode}")
        # Check if data dir was created
        data_dir = os.path.join("dist", "data")
        if os.path.exists(data_dir):
            print(f"Data directory was created: {data_dir}")
            for f in os.listdir(data_dir):
                print(f"  - {f}")
except Exception as e:
    print(f"Error: {e}")

# Check if database was created
db_path = os.path.join("dist", "data", "studydesk.db")
if os.path.exists(db_path):
    print(f"Database created: {db_path} ({os.path.getsize(db_path)} bytes)")
log_path = os.path.join("dist", "data", "logs", "studydesk.log")
if os.path.exists(log_path):
    print(f"Log file created: {log_path}")
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
    if "GUI launched" in content:
        print("Log confirms: GUI launched successfully!")
    if "Database initialized" in content:
        print("Log confirms: Database initialized!")
print("EXE test complete.")