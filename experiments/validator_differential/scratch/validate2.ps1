$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa = $asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$val = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$bf = [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static
$inst = $val.GetField("Instance",$bf).GetValue($null)
$loadFromFile = $dfa.GetMethod("LoadFromFile",[type[]]@([string]))
$validate = $val.GetMethod("Validate")

function Check([string]$path,[string]$label) {
  try {
    $args1 = New-Object object[] 1; $args1[0] = [string]$path
    $a = $loadFromFile.Invoke($null, $args1)
    if ($null -eq $a) { return "{0,-30} <load returned null>" -f $label }
    $args2 = New-Object object[] 1; $args2[0] = $a
    $r = $validate.Invoke($inst, $args2)
    return "{0,-30} {1} ({2})" -f $label, $r, [int]$r
  } catch {
    $m = $_.Exception; if ($m.InnerException) { $m = $m.InnerException }
    return "{0,-30} EXC {1}: {2}" -f $label, $m.GetType().Name, $m.Message
  }
}
$dir = "Z:\GitHub\rob-paprocki\extron-driver-convert\experiments\skeleton_i20\out"
Check "Z:\GitHub\rob-paprocki\extron-driver-convert\samples\1 Beyond Cameras\PTZ-IP12_IP20\pkp\1bynd_19_4743_v1_0_1.pkp" "DONOR (untouched)"
foreach ($f in @("1bynd_19_20020_v1_0_0.pkp","1bynd_19_20021_v1_0_0.pkp","1bynd_19_20022_v1_0_0.pkp","1bynd_19_20023_v1_0_0.pkp","1bynd_19_20030_v1_0_0.pkp","1bynd_19_20031_v1_0_0.pkp","1bynd_19_20032_v1_0_0.pkp")) {
  Check "$dir\$f" $f
}
