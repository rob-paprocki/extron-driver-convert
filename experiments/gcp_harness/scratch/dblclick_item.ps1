. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@(); foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts+=$t.Current.Name } }
  return ($parts -join ' / ')
}
$p=Get-Process GCP | Select-Object -First 1
[M]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 600
$win=Get-GCP
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
$want=$args[0]
foreach($l in $win.FindAll($TS::Descendants,$lc)){
  if((Label $l) -eq $want){
    $r=$l.Current.BoundingRectangle
    $x=[int]($r.X+$r.Width/2); $y=[int]($r.Y+$r.Height/2)
    Write-Output ("double-clicking '{0}' at ({1},{2})" -f $want,$x,$y)
    [M]::DblClick($x,$y)
    Start-Sleep -Seconds 3
    exit 0
  }
}
Write-Output "item '$want' not found"
