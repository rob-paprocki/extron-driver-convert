. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$all=$win.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
foreach($e in $all){
  $c=$e.Current
  $r=$c.BoundingRectangle
  Write-Output ("{0,-14} id='{1}' name='{2}' cls='{3}' rect=({4},{5},{6}x{7})" -f `
    $c.ControlType.ProgrammaticName.Replace('ControlType.',''),$c.AutomationId,$c.Name,$c.ClassName,
    [int]$r.X,[int]$r.Y,[int]$r.Width,[int]$r.Height)
}
