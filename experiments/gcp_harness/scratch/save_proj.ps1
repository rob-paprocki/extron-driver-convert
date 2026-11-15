. "$PSScriptRoot\uia_act.ps1"
. "$PSScriptRoot\mouse.ps1"
$p=Get-Process GCP | Select-Object -First 1
[M]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 500
$win=Get-GCP
$btn=Find-ById $win 'saveProjectBtn'
Write-Output ("save clicked: {0}" -f (Invoke-El $btn))
Start-Sleep -Seconds 3
$cond=New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty,$p.Id)
foreach($w in $AE::RootElement.FindAll($TS::Children,$cond)){ Write-Output ("  WIN '{0}'" -f $w.Current.Name) }
# a Save-As dialog is a native file dialog
$fd=$AE::RootElement.FindFirst($TS::Children,(New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Save As')))
if($fd){
  Write-Output "Save As dialog is open"
  $ec=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::Edit)
  $e=$fd.FindFirst($TS::Descendants,$ec)
  if($e){
    $vp=$null
    $e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$vp) | Out-Null
    $vp.SetValue($args[0]); Start-Sleep -Milliseconds 500
    $sb=Find-ByName $fd 'Save'
    if($sb){ Write-Output ("  save: {0}" -f (Invoke-El $sb)) }
  }
}
