$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa = $asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$ext = $asm.GetType("Extron.Configuration.Drivers.Extensions.DriverFileAssetExtensions")
$val = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$bf = [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static
$inst = $val.GetField("Instance",$bf).GetValue($null)
$load = $dfa.GetMethod("LoadFromFile",[type[]]@([string]))
$validate = $val.GetMethod("Validate")
$refresh = $ext.GetMethod("RefreshResourceHash")
$save = $dfa.GetMethod("SaveToFile", [type[]]@($asm.GetType("Extron.Configuration.Drivers.DriverFileAsset").GetInterfaces()[0], [string]))

$dir = "Z:\GitHub\rob-paprocki\extron-driver-convert\experiments\skeleton_i20\out"
$src = "$dir\1bynd_19_20023_v1_0_0.pkp"
$dst = "$dir\1bynd_19_20040_v1_0_0.pkp"

$a1 = New-Object object[] 1; $a1[0] = [string]$src
$asset = $load.Invoke($null, $a1)
$v = New-Object object[] 1; $v[0] = $asset
"before refresh : {0}" -f $validate.Invoke($inst, $v)

# show the stored hash dict before/after
$hp = $asset.GetType().GetProperty("ResourceHashDict")
$d0 = $hp.GetValue($asset)
"hash entries   : {0}" -f $d0.Count
foreach ($k in $d0.Keys) { "   {0} = {1}" -f $k, ([BitConverter]::ToString($d0[$k])) }

$r = New-Object object[] 1; $r[0] = $asset
$refresh.Invoke($null, $r) | Out-Null
"after refresh  : {0}" -f $validate.Invoke($inst, $v)
$d1 = $hp.GetValue($asset)
foreach ($k in $d1.Keys) { "   {0} = {1}" -f $k, ([BitConverter]::ToString($d1[$k])) }

# find a usable SaveToFile overload
$m = $dfa.GetMethods() | Where-Object { $_.Name -eq "SaveToFile" -and $_.GetParameters().Count -eq 2 } | Select-Object -First 1
$sa = New-Object object[] 2; $sa[0] = $asset; $sa[1] = [string]$dst
$m.Invoke($null, $sa) | Out-Null
"saved          : {0} ({1} bytes)" -f (Split-Path $dst -Leaf), (Get-Item $dst).Length

$a2 = New-Object object[] 1; $a2[0] = [string]$dst
$re = $load.Invoke($null, $a2)
$v2 = New-Object object[] 1; $v2[0] = $re
"reloaded       : {0}" -f $validate.Invoke($inst, $v2)
