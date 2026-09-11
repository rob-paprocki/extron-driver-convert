. "$PSScriptRoot\uia_act.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Driver Manager')
$dm=$AE::RootElement.FindFirst($TS::Descendants,$c)
$dc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::DataItem)
$rows=$dm.FindAll($TS::Descendants,$dc)
Write-Output ("rows: {0}" -f $rows.Count)
foreach($r in $rows){
  $cells=@()
  $cc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  foreach($t in $r.FindAll($TS::Descendants,$cc)){ if($t.Current.Name){ $cells += $t.Current.Name } }
  Write-Output ("  ROW: {0}" -f ($cells -join ' | '))
}
