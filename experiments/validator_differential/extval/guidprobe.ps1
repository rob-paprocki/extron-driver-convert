param([string]$Path)
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$valT=$asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$inst=$valT.GetField("Instance",'Public,Static').GetValue($null)
$valT.GetMethod("LoadDefaultFromResource").Invoke($inst,@()) | Out-Null
$tbl=$valT.GetField("a",'NonPublic,Instance,Public').GetValue($inst)
Write-Host ("guid table entries: " + $tbl.Count)
$la=New-Object object[] 1; $la[0]=[string]$Path
$a=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string])).Invoke($null,$la)
Write-Host ("hashdict count: " + $a.ResourceHashDict.Count)
foreach($r in $a.Manifest){
  $g=$r.Guid
  $h=[BitConverter]::ToString($r.GetContentHashCode()).Replace('-','').ToLower()
  $inTbl=$tbl.ContainsKey($g)
  $stored="-"
  if($inTbl){ $stored=[BitConverter]::ToString($tbl[$g]).Replace('-','').ToLower() }
  Write-Host ("  key='" + $r.Key + "' guid=" + $g + " inGuidTable=" + $inTbl + " match=" + ($stored -eq $h))
  Write-Host ("     computed=" + $h)
  Write-Host ("     tableval=" + $stored)
}
