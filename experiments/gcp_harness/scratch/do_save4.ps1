. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
Add-Type -AssemblyName System.Windows.Forms
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Save As')
$fd=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $fd){ Write-Output "no dialog"; exit 1 }
$h=[IntPtr]$fd.Current.NativeWindowHandle
[M]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 700
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
$e=$fd.FindFirst($TS::Descendants,$ec)
$r=$e.Current.BoundingRectangle
[M]::Click([int]($r.X+40),[int]($r.Y+$r.Height/2))
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("i20_verify")
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Seconds 6
$p=Get-Process GCP | Select-Object -First 1
Write-Output ("title: {0}" -f $p.MainWindowTitle)
