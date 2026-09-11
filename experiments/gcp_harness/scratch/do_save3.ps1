. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
# dismiss the Rename error if present
$rc=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Rename')
$rn=$AE::RootElement.FindFirst($TS::Descendants,$rc)
if($rn){
  $ok=Find-ByName $rn 'OK'
  if($ok){ $r=$ok.Current.BoundingRectangle; [M]::Click([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2)); Write-Output "dismissed Rename error" }
  Start-Sleep -Seconds 2
}
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Save As')
$fd=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $fd){ Write-Output "no Save As dialog"; exit 1 }
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
$e=$fd.FindFirst($TS::Descendants,$ec)
$vp=$null
$e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) | Out-Null
$vp.SetValue('i20_verify'); Start-Sleep -Milliseconds 600
$sb=Find-ByName $fd 'Save'
$r=$sb.Current.BoundingRectangle
[M]::Click([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))
Start-Sleep -Seconds 6
$p=Get-Process GCP | Select-Object -First 1
Write-Output ("title: {0}" -f $p.MainWindowTitle)
