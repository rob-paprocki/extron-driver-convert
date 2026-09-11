. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@(); foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts+=$t.Current.Name } }
  return ($parts -join ' ')
}
function PaneDump($win){
  $o=@()
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  foreach($t in $win.FindAll($TS::Descendants,$tc)){
    $rr=$t.Current.BoundingRectangle
    if($rr.X -gt 1580 -and $t.Current.Name -and $t.Current.Name -notmatch 'Expires|cti\.com|^Pro$'){ $o += ("{0}" -f $t.Current.Name) }
  }
  $ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
  foreach($e in $win.FindAll($TS::Descendants,$ec)){
    if($e.Current.BoundingRectangle.X -gt 1580){
      $vp=$null
      if($e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) -and $vp.Current.Value){ $o += ("<edit:{0}>" -f $vp.Current.Value) }
    }
  }
  return $o
}
$p=Get-Process GCP | Select-Object -First 1
[M]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 400
$win=Get-GCP
$cmd=$args[0]; $param=$args[1]
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
foreach($l in $win.FindAll($TS::Descendants,$lc)){
  if((Label $l) -match "^$cmd" -and $l.Current.BoundingRectangle.X -gt 400){
    $r=$l.Current.BoundingRectangle
    [M]::Click([int]($r.X+30),[int]($r.Y+$r.Height/2)); Start-Sleep -Seconds 2; break
  }
}
# click the parameter name text in the properties pane
$tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
foreach($t in $win.FindAll($TS::Descendants,$tc)){
  $rr=$t.Current.BoundingRectangle
  if($rr.X -gt 1580 -and $t.Current.Name -eq $param){
    [M]::Click([int]($rr.X+10),[int]($rr.Y+$rr.Height/2)); Start-Sleep -Seconds 2
    Write-Output ("=== {0} / {1} ===" -f $cmd,$param)
    foreach($x in (PaneDump $win)){ Write-Output ("   {0}" -f $x) }
    exit 0
  }
}
Write-Output "param '$param' not found in pane"
