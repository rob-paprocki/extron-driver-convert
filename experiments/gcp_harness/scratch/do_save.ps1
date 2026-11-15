. "$PSScriptRoot\uia_act.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Save As')
$fd=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $fd){ Write-Output "no Save As dialog"; exit 1 }
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
$e=$fd.FindFirst($TS::Descendants,$ec)
$vp=$null
$e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) | Out-Null
$vp.SetValue($args[0])
Start-Sleep -Milliseconds 700
$sb=Find-ByName $fd 'Save'
Write-Output ("save: {0}" -f (Invoke-El $sb))
Start-Sleep -Seconds 4
$p=Get-Process GCP | Select-Object -First 1
Write-Output ("title now: {0}" -f $p.MainWindowTitle)
