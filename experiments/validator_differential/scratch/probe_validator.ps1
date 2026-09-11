$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$t = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
"=== DriverAssetValidator ==="
$t.GetMethods([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::Instance) |
  Where-Object { $_.DeclaringType -eq $t } | ForEach-Object {
    "{0} {1}({2}) -> {3}" -f $(if($_.IsStatic){"static"}else{"      "}), $_.Name,
      (($_.GetParameters() | ForEach-Object { $_.ParameterType.Name + " " + $_.Name }) -join ", "),
      $_.ReturnType.Name
  }
"=== fields/consts ==="
$t.GetFields([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static) |
  ForEach-Object { "{0} {1} = {2}" -f $_.FieldType.Name, $_.Name, $(try{$_.GetValue($null)}catch{"?"}) }
