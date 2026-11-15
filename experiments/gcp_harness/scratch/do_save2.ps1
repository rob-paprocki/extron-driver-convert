. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Save As')
$fd=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $fd){ Write-Output "no Save As dialog"; exit 1 }
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
$e=$fd.FindFirst($TS::Descendants,$ec)
$vp=$null
$e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) | Out-Null
Write-Output ("filename box now: '{0}'" -f $vp.Current.Value)
$vp.SetValue($args[0]); Start-Sleep -Milliseconds 600
$sb=Find-ByName $fd 'Save'
$r=$sb.Current.BoundingRectangle
Write-Output ("clicking Save at ({0},{1})" -f [int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))
[M]::Click([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))
Start-Sleep -Seconds 5
$p=Get-Process GCP | Select-Object -First 1
Write-Output ("title: {0}" -f $p.MainWindowTitle)
