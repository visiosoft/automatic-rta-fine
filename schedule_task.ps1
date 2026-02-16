# PowerShell script to schedule the RTA automation
# This script creates a Windows Task Scheduler task to run the automation automatically

$TaskName = "RTA_Fines_Check"
$ScriptPath = "F:\MyRepo\FetchFine\run_headless.py"
$PythonExe = "F:\MyRepo\FetchFine\.venv\Scripts\python.exe"
$WorkingDir = "F:\MyRepo\FetchFine"

Write-Host "Creating Windows Scheduled Task for RTA Automation" -ForegroundColor Cyan
Write-Host "=" * 60

# Create the action
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkingDir

# Create triggers (you can customize these)
Write-Host "`nSelect when to run the automation:" -ForegroundColor Yellow
Write-Host "1. Daily at a specific time"
Write-Host "2. Every few hours"
Write-Host "3. Weekly"
Write-Host "4. Manual (run only when you trigger it)"

$choice = Read-Host "`nEnter your choice (1-4)"

switch ($choice) {
    "1" {
        $time = Read-Host "Enter time (e.g., 09:00 for 9 AM)"
        $Trigger = New-ScheduledTaskTrigger -Daily -At $time
        Write-Host "Task will run daily at $time" -ForegroundColor Green
    }
    "2" {
        $hours = Read-Host "Enter interval in hours (e.g., 6 for every 6 hours)"
        $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours $hours) -RepetitionDuration ([TimeSpan]::MaxValue)
        Write-Host "Task will run every $hours hours" -ForegroundColor Green
    }
    "3" {
        $time = Read-Host "Enter time (e.g., 09:00 for 9 AM)"
        $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $time
        Write-Host "Task will run weekly on Mondays at $time" -ForegroundColor Green
    }
    "4" {
        $Trigger = $null
        Write-Host "Task will only run when manually triggered" -ForegroundColor Green
    }
    default {
        Write-Host "Invalid choice. Creating manual trigger." -ForegroundColor Red
        $Trigger = $null
    }
}

# Register the task
try {
    if ($Trigger) {
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Automatically check RTA fines and save to MongoDB" -Force
    } else {
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Description "Manually check RTA fines and save to MongoDB" -Force
    }
    
    Write-Host "`n✓ Task created successfully!" -ForegroundColor Green
    Write-Host "`nTo manage the task:" -ForegroundColor Cyan
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for task: $TaskName"
    Write-Host "  - Or run manually: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host "`nTo remove the task: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    
} catch {
    Write-Host "`n✗ Error creating task: $_" -ForegroundColor Red
    Write-Host "You may need to run PowerShell as Administrator" -ForegroundColor Yellow
}
