. "$PSScriptRoot\uia_act.ps1"
Start-Sleep -Seconds 2
$p=Get-Process GCP | Select-Object -First 1
$cond=New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty,$p.Id)
foreach($w in $AE::RootElement.FindAll($TS::Children,$cond)){
  Write-Output ("WIN '{0}' cls={1}" -f $w.Current.Name,$w.Current.ClassName)
}
$win=Get-GCP
$all=$win.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
Write-Output ("main-window descendants: {0}" -f $all.Count)
# tree contents
$tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::TreeItem)
foreach($t in $win.FindAll($TS::Descendants,$tc)){ Write-Output ("  TREEITEM '{0}'" -f $t.Current.Name) }
# any list items (palette)
$lc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::ListItem)
$li=$win.FindAll($TS::Descendants,$lc)
Write-Output ("palette items: {0}" -f $li.Count)
foreach($l in $li){ if($l.Current.Name){ Write-Output ("  PALETTE '{0}'" -f $l.Current.Name) } }
