$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$t = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$m = $t.GetMethod("Validate")
$et = $m.ReturnType
"ErrorCode type: " + $et.FullName
foreach ($n in [Enum]::GetNames($et)) { "  {0,-40} = {1}" -f $n, [int][Enum]::Parse($et,$n) }
