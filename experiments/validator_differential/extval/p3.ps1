param([string]$Path)
$ErrorActionPreference='Stop'
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$loadM=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string]))
$la=New-Object object[] 1; $la[0]=[string]$Path
$a=$loadM.Invoke($null,$la)
Write-Host ("isnull=" + ($null -eq $a))
Write-Host ("t=" + $a.GetType().FullName)
