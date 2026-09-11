. "$PSScriptRoot\uia_lib.ps1"

function Find-ById($root,$id){
  $c=New-Object System.Windows.Automation.PropertyCondition($AE::AutomationIdProperty,$id)
  return $root.FindFirst($TS::Descendants,$c)
}
function Find-ByName($root,$name){
  $c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$name)
  return $root.FindFirst($TS::Descendants,$c)
}
function Invoke-El($el){
  $p=$null
  if($el.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern,[ref]$p)){ $p.Invoke(); return $true }
  if($el.TryGetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern,[ref]$p)){ $p.Toggle(); return $true }
  if($el.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern,[ref]$p)){ $p.Select(); return $true }
  if($el.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$p)){ $p.Expand(); return $true }
  return $false
}
