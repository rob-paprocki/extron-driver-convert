param([string]$Path)
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$loadM=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string]))
$la=New-Object object[] 1
$la[0]=[string]$Path
$asset=$loadM.Invoke($null,$la)
Write-Host ("assetnull  : " + ($null -eq $asset))
Write-Host ("Filename   : " + $asset.Filename)
Write-Host ("Guid       : " + $asset.Guid)
Write-Host ("Name       : " + $asset.Name)
$rhd=$asset.ResourceHashDict
if($null -eq $rhd){ Write-Host "ResourceHashDict: NULL" }
else{
  Write-Host ("ResourceHashDict count: " + $rhd.Count)
  foreach($k in $rhd.Keys){ Write-Host ("   dictkey: '" + $k + "' -> " + [BitConverter]::ToString($rhd[$k]).Replace('-','').ToLower()) }
}
$mf=$asset.Manifest
if($null -eq $mf){ Write-Host "Manifest: NULL" }
else{
  Write-Host ("Manifest type: " + $mf.GetType().FullName)
  Write-Host ("Manifest name: " + $mf.Name)
  $i=0
  foreach($r in $mf){
    $i=$i+1
    $key="?"
    try{ $key=$r.Key }catch{ $key="<throw>" }
    $g="?"
    try{ $g=$r.Guid }catch{ $g="<throw>" }
    $ct="?"
    try{
      $c=$r.Content
      if($null -eq $c){ $ct="null" } else { $ct=$c.GetType().FullName }
    }catch{ $ct="<throw>" }
    $h="?"
    try{
      $hb=$r.GetContentHashCode()
      if($null -eq $hb){ $h="null" } else { $h=[BitConverter]::ToString($hb).Replace('-','').ToLower() }
    }catch{ $h=("<throw:"+$_.Exception.GetBaseException().GetType().Name+">") }
    Write-Host ("  res[" + $i + "] type=" + $r.GetType().Name + " key='" + $key + "' guid=" + $g + " content=" + $ct + " hash=" + $h)
  }
  Write-Host ("Manifest resource count: " + $i)
}
$children=$asset.Children
if($null -ne $children){
  Write-Host ("Children count: " + $children.Count)
  foreach($ch in $children){ Write-Host ("   child: " + $ch.GetType().Name + " name='" + $ch.Name + "'") }
}
