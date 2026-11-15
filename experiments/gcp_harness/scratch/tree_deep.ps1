. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$all=$win.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
Write-Output ("total descendants: {0}" -f $all.Count)
foreach($e in $all){
  $ct=$e.Current.ControlType.ProgrammaticName.Replace('ControlType.','')
  $id=$e.Current.AutomationId; $n=$e.Current.Name
  if($ct -in @('Button','MenuItem','List','ListItem','Tree','TreeItem','Tab','TabItem','Hyperlink','SplitButton')){
    if($id -or $n){ Write-Output ("{0,-12} id='{1}' name='{2}'" -f $ct,$id,$n) }
  }
}
