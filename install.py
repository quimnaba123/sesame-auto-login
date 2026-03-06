import sys
import subprocess
import os
from datetime import datetime
import json
# Add your other imports here...

def install_startup_task():
    """Create scheduled task that runs at user logon"""
    #script_path = os.path.abspath(__file__)
    script_path = 'C:\Git\sesame-auto-login\main.py'  # Change this to the actual path of your script
    python_exe = sys.executable
    username = os.environ['USERNAME']
    task_name = "Sesame_AutoCheckin"
    
    # Get Windows password if needed (for logon type password)
    with open('PrivateData.json') as f:
        pvdata = json.load(f)
    win_pwd = pvdata["windows_pwd"]
    
    ps_command = f"""
    $action = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '"{script_path}"' -WorkingDirectory '{os.path.dirname(script_path)}'
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User '{username}'
    $principal = New-ScheduledTaskPrincipal -UserId '{username}' -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    
    Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    Write-Host "Task '{task_name}' created to run at logon"
    """
    
    print("\n🔧 Installing Sesame Clock-In to run at Windows startup...")
    result = subprocess.run(['powershell', '-Command', ps_command], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Successfully installed! The script will run automatically every time you log in.")
        print("📝 Task name: SesameClockIn_Startup")
        print("   You can view/modify it in Task Scheduler if needed.\n")
    else:
        print(f"❌ Failed to install: {result.stderr}")

def uninstall_startup_task():
    """Remove the scheduled task"""
    task_name = "SesameClockIn_Startup"
    
    print("\n🔧 Uninstalling Sesame Clock-In startup task...")
    result = subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Successfully uninstalled!\n")
    else:
        print(f"❌ Failed to uninstall (task might not exist): {result.stderr}")