# PowerShell script to schedule the RTA automation to run every 3 hours
# This creates a Windows Task Scheduler task

$TaskName = "RTA_Fines_Check_Every_3Hours"
$ScriptPath = "F:\MyRepo\FetchFine\run_headless.py"
$PythonExe = "F:\MyRepo\FetchFine\.venv\Scripts\python.exe"
$WorkingDir = "F:\MyRepo\FetchFine"

Write-Host "Creating Windows Scheduled Task for RTA Automation" -ForegroundColor Cyan
Write-Host "Task will run every 3 hours" -ForegroundColor Yellow
Write-Host "============================================================"

# Create the action
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkingDir

# Create trigger - runs every 3 hours indefinitely
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 3)

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Automatically check RTA fines every 3 hours and save to MongoDB" -Force
    
    Write-Host ""
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Every 3 hours" -ForegroundColor White
    Write-Host "  Mode: Headless (background)" -ForegroundColor White
    Write-Host ""
    Write-Host "Next run times:" -ForegroundColor Cyan
    
    # Show next 5 run times
    $now = Get-Date
    for ($i = 0; $i -lt 5; $i++) {
        $nextRun = $now.AddHours($i * 3)
        $number = $i + 1
        Write-Host "  $number. $($nextRun.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "To manage the task:" -ForegroundColor Cyan
    Write-Host "  - Open Task Scheduler: taskschd.msc" -ForegroundColor White
    Write-Host "  - Run manually: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  - View status: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  - Remove task: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "Error creating task: $_" -ForegroundColor Red
    Write-Host "You may need to run PowerShell as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================"
