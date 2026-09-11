$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
Add-Type -Path "$gcp\Extron.Configuration.Contracts.dll" -ErrorAction SilentlyContinue
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa = $asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$val = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$inst = $val.GetField("Instance",[System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static).GetValue($null)
$loadFromFile = $dfa.GetMethod("LoadFromFile",[type[]]@([string]))
$validate = $val.GetMethod("Validate")

$dir = "Z:\GitHub\rob-paprocki\extron-driver-convert\experiments\skeleton_i20\out"
$files = @(
  "1bynd_19_20020_v1_0_0.pkp","1bynd_19_20021_v1_0_0.pkp",
  "1bynd_19_20022_v1_0_0.pkp","1bynd_19_20023_v1_0_0.pkp",
  "1bynd_19_20030_v1_0_0.pkp","1bynd_19_20031_v1_0_0.pkp","1bynd_19_20032_v1_0_0.pkp")
"{0,-32} {1}" -f "package","Validate()"
foreach ($f in $files) {
  $p = Join-Path $dir $f
  if (-not (Test-Path $p)) { "{0,-32} <missing>" -f $f; continue }
  try {
    $a = $loadFromFile.Invoke($null, @($p))
    $r = $validate.Invoke($inst, @($a))
    "{0,-32} {1} ({2})" -f $f, $r, [int]$r
  } catch { "{0,-32} EXC: {1}" -f $f, $_.Exception.InnerException.Message }
}
# and the untouched donor as a control
$donor = "Z:\GitHub\rob-paprocki\extron-driver-convert\samples\1 Beyond Cameras\PTZ-IP12_IP20\pkp\1bynd_19_4743_v1_0_1.pkp"
$a = $loadFromFile.Invoke($null, @($donor))
"{0,-32} {1} ({2})" -f "DONOR 1bynd_19_4743", $validate.Invoke($inst,@($a)), [int]$validate.Invoke($inst,@($a))
