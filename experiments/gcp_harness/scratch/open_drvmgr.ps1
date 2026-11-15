. "$PSScriptRoot\uia_act.ps1"
$win=Get-GCP
$btn=Find-ById $win 'drvMgrBtn'
if(-not $btn){ Write-Output "drvMgrBtn NOT FOUND"; exit 1 }
Write-Output ("invoking drvMgrBtn: {0}" -f (Invoke-El $btn))
Start-Sleep -Seconds 4
$p=Get-Process GCP | Select-Object -First 1
$cond=New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty,$p.Id)
$wins=$AE::RootElement.FindAll($TS::Children,$cond)
foreach($w in $wins){ Write-Output ("  WIN '{0}' cls={1}" -f $w.Current.Name,$w.Current.ClassName) }
