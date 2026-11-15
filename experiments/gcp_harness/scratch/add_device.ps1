. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$mc=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,[System.Windows.Automation.ControlType]::MenuItem)
$items=$win.FindAll($TS::Descendants,$mc)
$target=$null
foreach($m in $items){
  $r=$m.Current.BoundingRectangle
  Write-Output ("MENUITEM name='{0}' rect=({1},{2},{3}x{4})" -f $m.Current.Name,[int]$r.X,[int]$r.Y,[int]$r.Width,[int]$r.Height)
  if($r.Y -gt 60 -and $r.Y -lt 100 -and $r.X -lt 275){ $target=$m }
}
if(-not $target){ Write-Output "no add-device menuitem found"; exit 1 }
$r=$target.Current.BoundingRectangle
Write-Output ("--> invoking the one at ({0},{1})" -f [int]$r.X,[int]$r.Y)
$ep=$null
if($target.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$ep)){
  $ep.Expand(); Start-Sleep -Seconds 2
  foreach($k in $target.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)){
    if($k.Current.ControlType.ProgrammaticName -match 'MenuItem'){
      Write-Output ("   SUB '{0}' enabled={1}" -f $k.Current.Name,$k.Current.IsEnabled)
    }
  }
} else { Write-Output ("   invoke: {0}" -f (Invoke-El $target)) }
