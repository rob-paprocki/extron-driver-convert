. "$PSScriptRoot\uia_act.ps1"
function Label($el){
  $tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
  $parts=@()
  foreach($t in $el.FindAll($TS::Descendants,$tc)){ if($t.Current.Name){ $parts += $t.Current.Name } }
  return ($parts -join ' / ')
}
$win=Get-GCP
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
$items=$win.FindAll($TS::Descendants,$lc)
$want=$args[0]
$i=0
foreach($l in $items){
  $lab=Label $l
  Write-Output ("  [{0}] {1}" -f $i,$lab)
  if($want -and $lab -match $want){
    $sp=$null
    if($l.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern,[ref]$sp)){ $sp.Select(); Write-Output ("  --> selected '{0}'" -f $lab) }
  }
  $i++
}
