. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@(); foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts+=$t.Current.Name } }
  return ($parts -join ' ')
}
function PropText($win){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $o=@()
  foreach($t in $win.FindAll($TS::Descendants,$tc)){
    $rr=$t.Current.BoundingRectangle
    if($rr.X -gt 1580 -and $t.Current.Name -and $t.Current.Name -notmatch 'Expires|cti.com|^Pro$'){ $o+=$t.Current.Name }
  }
  return $o
}
$p=Get-Process GCP | Select-Object -First 1
[M]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 400
$win=Get-GCP
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
$want=$args[0]
foreach($l in $win.FindAll($TS::Descendants,$lc)){
  if((Label $l) -match "^$want" -and $l.Current.BoundingRectangle.X -gt 400){
    $r=$l.Current.BoundingRectangle
    [M]::Click([int]($r.X+30),[int]($r.Y+$r.Height/2)); Start-Sleep -Seconds 2; break
  }
}
# now click each DataItem row in the Parameters grid on the right
$dc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::DataItem)
$rows=@()
foreach($d in $win.FindAll($TS::Descendants,$dc)){ if($d.Current.BoundingRectangle.X -gt 1580){ $rows += $d } }
Write-Output ("parameter rows: {0}" -f $rows.Count)
foreach($row in $rows){
  $r=$row.Current.BoundingRectangle
  [M]::Click([int]($r.X+40),[int]($r.Y+$r.Height/2)); Start-Sleep -Milliseconds 1200
  $txt = PropText $win
  Write-Output ("--- param row at y={0}: {1}" -f [int]$r.Y, ($txt -join ' | '))
}
