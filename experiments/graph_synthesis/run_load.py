import subprocess, os, sys
if len(sys.argv) < 2:
    print("usage: run_load.py <pkp>"); sys.exit(2)
ps32 = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
script = os.path.abspath("experiments/gcp_harness/Load-Package.ps1")
pkp = os.path.abspath(sys.argv[1])
cp = subprocess.run([ps32, "-ExecutionPolicy", "Bypass", "-File", script,
                     "-Path", pkp, "-Deserialize", "-Commands"],
                    capture_output=True, text=True, timeout=90)
print(cp.stdout)
if cp.stderr: print("STDERR:", cp.stderr)
print("rc:", cp.returncode)
