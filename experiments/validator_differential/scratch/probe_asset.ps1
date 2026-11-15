$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$bf = [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::Instance
foreach ($n in @("Extron.Configuration.Drivers.DriverFileAsset",
                 "Extron.Configuration.Drivers.Extensions.DriverFileAssetExtensions")) {
  $t = $asm.GetType($n)
  "=== $n ==="
  $t.GetProperties($bf) | Where-Object { $_.DeclaringType -eq $t } | ForEach-Object { "  prop {0} {1}" -f $_.PropertyType.Name, $_.Name }
  $t.GetMethods($bf) | Where-Object { $_.DeclaringType -eq $t -and $_.Name -notmatch "^(get_|set_)" } | Select-Object -First 22 | ForEach-Object {
    "  {0}({1}) -> {2}" -f $_.Name, (($_.GetParameters()|ForEach-Object{$_.ParameterType.Name}) -join ","), $_.ReturnType.Name }
}
"=== embedded resources in Drivers.dll ==="
$asm.GetManifestResourceNames()
