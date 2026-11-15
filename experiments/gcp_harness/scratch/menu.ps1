. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$menuName=$args[0]
$m=Find-ByName $win $menuName
if(-not $m){ Write-Output "menu $menuName not found"; exit 1 }
$ep=$null
if($m.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$ep)){
  $ep.Expand(); Start-Sleep -Milliseconds 900
  $kids=$m.FindAll($TS::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
  foreach($k in $kids){
    if($k.Current.ControlType.ProgrammaticName -match 'MenuItem'){
      Write-Output ("  ITEM '{0}' enabled={1}" -f $k.Current.Name,$k.Current.IsEnabled)
    }
  }
  $ep.Collapse()
} else { Write-Output "no ExpandCollapse on $menuName" }
