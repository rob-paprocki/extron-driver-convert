. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
# any window anywhere with Driver Manager in the name
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,'Driver Manager')
$dm=$AE::RootElement.FindFirst($TS::Descendants,$c)
if($dm){ Write-Output ("FOUND Driver Manager cls={0} enabled={1}" -f $dm.Current.ClassName,$dm.Current.IsEnabled) }
else { Write-Output "not found by exact name; scanning windows" }
$p=Get-Process GCP | Select-Object -First 1
$cond=New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty,$p.Id)
$all=$AE::RootElement.FindAll($TS::Descendants, $cond)
Write-Output ("descendant elements in GCP process: {0}" -f $all.Count)
$seen=@{}
foreach($e in $all){
  $n=$e.Current.Name
  if($n -and ($n -match 'Driver|Manufacturer|Model|Showing')){
    $k="$($e.Current.ControlType.ProgrammaticName)|$n"
    if(-not $seen.ContainsKey($k)){ $seen[$k]=1; Write-Output ("  {0} '{1}' id={2}" -f $e.Current.ControlType.ProgrammaticName.Replace('ControlType.',''),$n,$e.Current.AutomationId) }
  }
}
