. "$PSScriptRoot\uia_act.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Driver Manager')
$dm=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $dm){ Write-Output "DM not open"; exit 1 }

# find the search edit box
$ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
$edits=$dm.FindAll($TS::Descendants,$ec)
Write-Output ("edit boxes: {0}" -f $edits.Count)
$i=0
foreach($e in $edits){ Write-Output ("  edit[{0}] id='{1}' name='{2}'" -f $i,$e.Current.AutomationId,$e.Current.Name); $i++ }

if($edits.Count -gt 0){
  $box=$edits[0]
  $vp=$null
  if($box.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp)){
    $vp.SetValue('IV-CAM')
    Write-Output "typed 'IV-CAM' into edit[0]"
    Start-Sleep -Seconds 3
  } else { Write-Output "edit[0] has no ValuePattern" }
}
$tc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
foreach($t in $dm.FindAll($TS::Descendants,$tc)){
  if($t.Current.Name -match 'Showing'){ Write-Output ("STATUS: {0}" -f $t.Current.Name) }
}
