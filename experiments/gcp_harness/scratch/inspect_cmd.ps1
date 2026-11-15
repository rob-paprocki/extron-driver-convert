. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@(); foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts+=$t.Current.Name } }
  return ($parts -join ' ')
}
$p=Get-Process GCP | Select-Object -First 1
[M]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 400
$win=Get-GCP
$want=$args[0]
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
$hit=$null
foreach($l in $win.FindAll($TS::Descendants,$lc)){
  $lab=Label $l
  if($lab -match "^$want" -and $l.Current.BoundingRectangle.X -gt 400){ $hit=$l; break }
}
if(-not $hit){ Write-Output "command '$want' row not found"; exit 1 }
$r=$hit.Current.BoundingRectangle
[M]::Click([int]($r.X+30),[int]($r.Y+$r.Height/2))
Start-Sleep -Seconds 2
# read the Properties pane (right side, X > 1580)
$tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
Write-Output ("=== PROPERTIES for '{0}' ===" -f $want)
foreach($t in $win.FindAll($TS::Descendants,$tc)){
  $rr=$t.Current.BoundingRectangle
  if($rr.X -gt 1580 -and $t.Current.Name){ Write-Output ("   {0}" -f $t.Current.Name) }
}
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
foreach($e in $win.FindAll($TS::Descendants,$ec)){
  $rr=$e.Current.BoundingRectangle
  if($rr.X -gt 1580){
    $vp=$null
    if($e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp)){ Write-Output ("   [edit] {0}" -f $vp.Current.Value) }
  }
}
