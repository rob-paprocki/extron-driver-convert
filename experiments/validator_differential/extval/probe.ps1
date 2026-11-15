param([string]$Path)
$ErrorActionPreference='Stop'
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$loadM=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string]))
$la=New-Object object[] 1; $la[0]=[string]$Path
$a=$loadM.Invoke($null,$la)
Write-Host ("asset type : " + $a.GetType().FullName)
Write-Host ("Filename   : " + $a.Filename)
Write-Host ("Guid       : " + $a.Guid)
Write-Host ("Name       : " + $a.Name)
$rhd=$a.ResourceHashDict
if($null -eq $rhd){ Write-Host "ResourceHashDict: NULL" }
else{
  Write-Host ("ResourceHashDict count: " + $rhd.Count)
  foreach($k in $rhd.Keys){ Write-Host ("   dictkey: '" + $k + "' -> " + [BitConverter]::ToString($rhd[$k]).Replace('-','').ToLower()) }
}
$m=$a.Manifest
if($null -eq $m){ Write-Host "Manifest: NULL" }
else{
  Write-Host ("Manifest type: " + $m.GetType().FullName)
  Write-Host ("Manifest name: " + $m.Name)
  $i=0
  foreach($r in $m){
    $i++
    $key=$null; try{$key=$r.Key}catch{$key="<throw>"}
    $g=$null; try{$g=$r.Guid}catch{$g="<throw>"}
    $ct=$null; try{ $c=$r.Content; if($null -eq $c){$ct="null"} else {$ct=$c.GetType().FullName + " len=" + $(try{$c.Length}catch{"?"})} }catch{$ct="<throw>"}
    $h=$null; try{ $hb=$r.GetContentHashCode(); if($null -eq $hb){$h="null"}else{$h=[BitConverter]::ToString($hb).Replace('-','').ToLower()} }catch{$h="<throw: "+$_.Exception.GetBaseException().GetType().Name+">"}
    Write-Host ("  res[$i] type=" + $r.GetType().Name + " key='" + $key + "' guid=" + $g + " content=" + $ct + " hash=" + $h)
  }
  Write-Host ("Manifest resource count: " + $i)
}
