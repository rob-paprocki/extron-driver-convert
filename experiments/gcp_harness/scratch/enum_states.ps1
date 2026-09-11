. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@(); foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts+=$t.Current.Name } }
  return ($parts -join ' ')
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
$tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
foreach($t in $win.FindAll($TS::Descendants,$tc)){
  $rr=$t.Current.BoundingRectangle
  if($rr.X -gt 1580 -and $t.Current.Name -eq $param){
    [M]::Click([int]($rr.X+10),[int]($rr.Y+$rr.Height/2)); Start-Sleep -Seconds 2; break
  }
}
# expand every combobox in the properties pane and list items
$cc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ComboBox)
foreach($cb in $win.FindAll($TS::Descendants,$cc)){
  if($cb.Current.BoundingRectangle.X -le 1580){ continue }
  $ep=$null
  if($cb.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$ep)){
    $ep.Expand(); Start-Sleep -Milliseconds 900
    $items=$cb.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)))
    $names=@(); foreach($it in $items){ if($it.Current.Name){ $names += $it.Current.Name } }
    Write-Output ("{0}/{1} dropdown -> {2}" -f $cmd,$param,($names -join ', '))
    $ep.Collapse()
  }
}
