. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Driver Manager')
$dm=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $dm){ Write-Output "DM not open"; exit 1 }
$box=Find-ById $dm 'searchTextBox'
$vp=$null
$box.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) | Out-Null
$vp.SetValue($args[0]); Start-Sleep -Seconds 3

$dc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::DataItem)
$rows=$dm.FindAll($TS::Descendants,$dc)
Write-Output ("rows: {0}" -f $rows.Count)
$target=$null
foreach($r in $rows){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $cells=@(); foreach($t in $r.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $cells+=$t.Current.Name } }
  Write-Output ("  ROW: {0}" -f ($cells -join ' | '))
  if(($cells -join '|') -match $args[1]){ $target=$r }
}
if(-not $target){ Write-Output "target row not found"; exit 1 }
$sp=$null
if($target.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern,[ref]$sp)){ $sp.Select(); Write-Output "row selected" }
Start-Sleep -Seconds 1
$ok=Find-ByName $dm 'OK'
if($ok -and $ok.Current.IsEnabled){ Write-Output ("OK: {0}" -f (Invoke-El $ok)) }
else { Write-Output "OK not available; double-clicking row"
  $r=$target.Current.BoundingRectangle
  [M]::DblClick([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))
}
Start-Sleep -Seconds 4
