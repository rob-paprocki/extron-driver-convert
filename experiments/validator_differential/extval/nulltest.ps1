$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$valT=$asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$inst=$valT.GetField("Instance",'Public,Static').GetValue($null)
$va=New-Object object[] 1; $va[0]=$null
try{ $r=$valT.GetMethod("Validate").Invoke($inst,$va); Write-Host ("Validate(null) = " + [int]$r + " " + $r) }
catch{ $e=$_.Exception.GetBaseException(); Write-Host ("Validate(null) THREW " + $e.GetType().FullName + ": " + $e.Message) }
# what does the guid table look like before/after LoadDefaultFromResource?
$f=$valT.GetFields('NonPublic,Instance,Public')
foreach($fi in $f){ $v=$fi.GetValue($inst); $d="null"; if($null -ne $v){ $d=$v.GetType().Name; try{$d=$d+" count="+$v.Count}catch{} }; Write-Host ("  field before: " + $fi.Name + " = " + $d) }
$valT.GetMethod("LoadDefaultFromResource").Invoke($inst,@()) | Out-Null
Write-Host "-- after LoadDefaultFromResource --"
foreach($fi in $f){ $v=$fi.GetValue($inst); $d="null"; if($null -ne $v){ $d=$v.GetType().Name; try{$d=$d+" count="+$v.Count}catch{} }; Write-Host ("  field after : " + $fi.Name + " = " + $d) }
