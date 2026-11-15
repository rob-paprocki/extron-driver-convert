. "$PSScriptRoot\uia_act.ps1"
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Driver Manager')
$dm=$AE::RootElement.FindFirst($TS::Descendants,$c)
if($dm){
  $ok=Find-ByName $dm 'OK'
  if($ok){ Write-Output ("closing DM: {0}" -f (Invoke-El $ok)) }
  else {
    $wp=$null
    if($dm.TryGetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern,[ref]$wp)){ $wp.Close(); Write-Output "closed via WindowPattern" }
  }
  Start-Sleep -Seconds 2
}
$win=Get-GCP
# what's in the project tree / palette area?
$bc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Button)
foreach($b in $win.FindAll($TS::Descendants,$bc)){
  $id=$b.Current.AutomationId; $n=$b.Current.Name
  if($id -or $n){ Write-Output ("BTN id='{0}' name='{1}' enabled={2}" -f $id,$n,$b.Current.IsEnabled) }
}
