$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [System.Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa = $asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$val = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$bf = [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static
$inst = $val.GetField("Instance",$bf).GetValue($null)
$load = $dfa.GetMethod("LoadFromFile",[type[]]@([string]))
$validate = $val.GetMethod("Validate")
function Check([string]$path,[string]$label) {
  try {
    $a1 = New-Object object[] 1; $a1[0] = [string]$path
    $a = $load.Invoke($null,$a1)
    $a2 = New-Object object[] 1; $a2[0] = $a
    "{0,-30} {1}" -f $label, $validate.Invoke($inst,$a2)
  } catch { $m=$_.Exception; if($m.InnerException){$m=$m.InnerException}; "{0,-30} EXC {1}" -f $label,$m.Message }
}
$dir="Z:\GitHub\rob-paprocki\extron-driver-convert\experiments\skeleton_i20\out"
foreach ($f in (Get-ChildItem $dir -Filter *.pkp | Sort-Object Name)) { Check $f.FullName $f.Name }
