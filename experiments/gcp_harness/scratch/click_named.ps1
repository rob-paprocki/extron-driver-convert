. "$PSScriptRoot\uia_act.ps1"
$winName=$args[0]; $btnName=$args[1]
$c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$winName)
$w=$AE::RootElement.FindFirst($TS::Descendants,$c)
if(-not $w){ Write-Output "window '$winName' not found"; exit 1 }
$b=Find-ByName $w $btnName
if(-not $b){ Write-Output "button '$btnName' not found"; exit 1 }
Write-Output ("clicking '{0}': {1}" -f $btnName,(Invoke-El $b))
