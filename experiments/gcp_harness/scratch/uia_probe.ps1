Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms
$procs = Get-Process | Where-Object { $_.MainWindowTitle -and $_.ProcessName -match 'GCP|Global|Extron' }
foreach($p in $procs){ Write-Output ("PROC {0} pid={1} title={2}" -f $p.ProcessName,$p.Id,$p.MainWindowTitle) }
if(-not $procs){ Write-Output "NO GCP PROCESS"; exit 0 }
$root=[System.Windows.Automation.AutomationElement]::RootElement
$cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procs[0].Id)
$win=$root.FindAll([System.Windows.Automation.TreeScope]::Children,$cond)
Write-Output ("top-level windows for pid {0}: {1}" -f $procs[0].Id, $win.Count)
foreach($w in $win){
  Write-Output ("  WIN name='{0}' class={1} enabled={2}" -f $w.Current.Name,$w.Current.ClassName,$w.Current.IsEnabled)
}
