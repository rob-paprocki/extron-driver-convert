. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$f=Find-ByName $win 'File'
$ep=$null; $f.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$ep) | Out-Null
$ep.Expand(); Start-Sleep -Milliseconds 900
$item=$null
foreach($k in $f.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)){
  if($k.Current.Name -eq 'New Project (Pro)' -and $k.Current.ControlType.ProgrammaticName -match 'MenuItem'){ $item=$k; break }
}
if(-not $item){ Write-Output "New Project (Pro) not found"; exit 1 }
Write-Output ("invoke New Project (Pro): {0}" -f (Invoke-El $item))
Start-Sleep -Seconds 4
$p=Get-Process GCP | Select-Object -First 1
$cond=New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty,$p.Id)
foreach($w in $AE::RootElement.FindAll($TS::Children,$cond)){ Write-Output ("  WIN '{0}'" -f $w.Current.Name) }
$win2=Get-GCP
Write-Output ("descendants now: {0}" -f $win2.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition).Count)
