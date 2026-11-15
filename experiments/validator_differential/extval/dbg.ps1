param([string]$Path)
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$loadM=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string]))
$la=New-Object object[] 1; $la[0]=[string]$Path
$a=$loadM.Invoke($null,$la)
Write-Host ("isnull=" + ($null -eq $a))
if($null -ne $a){ Write-Host ("type=" + $a.GetType().FullName) }
$valT=$asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$inst=$valT.GetField("Instance",'Public,Static').GetValue($null)
$va=New-Object object[] 1; $va[0]=$a
$r=$valT.GetMethod("Validate").Invoke($inst,$va)
Write-Host ("validate=" + [int]$r + " " + $r)
