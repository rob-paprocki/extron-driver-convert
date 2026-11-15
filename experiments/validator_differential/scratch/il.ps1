$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$t = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$bf = [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Static
foreach ($name in @("Validate","ComputeHash")) {
  $m = $t.GetMethod($name, $bf)
  $body = $m.GetMethodBody()
  $il = $body.GetILAsByteArray()
  "=== $name : IL {0} bytes, maxstack {1}, locals {2} ===" -f $il.Length, $body.MaxStackSize, $body.LocalVariables.Count
  foreach ($lv in $body.LocalVariables) { "   local[{0}] {1}" -f $lv.LocalIndex, $lv.LocalType.Name }
  ($il | ForEach-Object { $_.ToString("X2") }) -join " "
  ""
}
