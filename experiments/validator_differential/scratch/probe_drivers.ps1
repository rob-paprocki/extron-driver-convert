$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
"loaded: " + $asm.FullName
$types = $asm.GetTypes()
"types: " + $types.Count
$types | Where-Object { $_.Name -match "Load|Read|Valid|Package|Serial|Driver(File|Manager|Repo)" } |
  Select-Object -First 30 -ExpandProperty FullName
