$ErrorActionPreference="Stop"
$gcp = "C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm = [Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa = $asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$val = $asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$bf = [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Static
$inst = $val.GetField("Instance",$bf).GetValue($null)
$load = $dfa.GetMethod("LoadFromFile",[type[]]@([string]))
$validate = $val.GetMethod("Validate")
function Check([string]$p) {
  try {
    $a1 = New-Object object[] 1; $a1[0] = [string]$p
    $a = $load.Invoke($null,$a1)
    if ($null -eq $a) { return "LoadFromFile->null" }
    $a2 = New-Object object[] 1; $a2[0] = $a
    return [string]$validate.Invoke($inst,$a2)
  } catch { $m=$_.Exception; if($m.InnerException){$m=$m.InnerException}; return "EXC "+$m.Message }
}
$t = "C:\Users\robp\.claude\jobs\a721b700\tmp\eirtest"
foreach ($f in @("bad_ondisk.eir","bad_plain.pkp")) { "{0,-20} {1}" -f $f, (Check "$t\$f") }
foreach ($f in @("extr_10_397_v1_0_4.pkp","extr_1_789_v1_0_2.pkp","extr_8_89_v1_0_0.pkp")) {
  "{0,-26} {1}" -f $f, (Check "C:\Users\Public\Documents\extron\Driver3\$f") }
