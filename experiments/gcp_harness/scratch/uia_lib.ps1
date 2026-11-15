Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$AE=[System.Windows.Automation.AutomationElement]
$TS=[System.Windows.Automation.TreeScope]

function Get-GCP {
  $p = Get-Process GCP -ErrorAction SilentlyContinue | Select-Object -First 1
  if(-not $p){ throw "GCP not running" }
  $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $p.Id)
  $wins = $AE::RootElement.FindAll($TS::Children, $cond)
  # prefer the main window (has a title)
  foreach($w in $wins){ if($w.Current.Name -match 'Global Configurator'){ return $w } }
  if($wins.Count -gt 0){ return $wins[0] }
  throw "no GCP window"
}

function Dump-Tree($el, $depth, $max) {
  if($depth -gt $max){ return }
  $kids = $el.FindAll($TS::Children, [System.Windows.Automation.Condition]::TrueCondition)
  foreach($k in $kids){
    $c=$k.Current
    $pad = ' ' * ($depth*2)
    if($c.Name -or $c.AutomationId){
      Write-Output ("{0}[{1}] name='{2}' id='{3}' cls='{4}' enabled={5}" -f $pad,$c.ControlType.ProgrammaticName.Replace('ControlType.',''),$c.Name,$c.AutomationId,$c.ClassName,$c.IsEnabled)
    }
    Dump-Tree $k ($depth+1) $max
  }
}
