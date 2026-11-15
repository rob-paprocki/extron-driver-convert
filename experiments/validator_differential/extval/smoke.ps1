$ErrorActionPreference='Stop'
Write-Host ("PtrSize=" + [IntPtr]::Size)
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfa=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$val=$asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
Write-Host ("DFA=" + $dfa); Write-Host ("VAL=" + $val)
$dfa.GetMethods('Public,Static,FlattenHierarchy') | %{ Write-Host ("  M: " + $_.ToString()) }
Write-Host "--- validator members ---"
$val.GetMembers('Public,Static,Instance,FlattenHierarchy,DeclaredOnly') | %{ Write-Host ("  " + $_.MemberType + ": " + $_.ToString()) }
