$ErrorActionPreference='Continue'
$base='C:\Program Files (x86)\Extron\GCP\'
$a=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll')
$mod=$a.GetModules()[0]
$bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
$sf=$a.GetType('Extron.Configuration.Drivers.DriverDescriptorAsset').GetMethod('set_Filename',$bf)
$gf=$a.GetType('Extron.Configuration.Drivers.DriverDescriptorAsset').GetMethod('get_Filename',$bf)
Write-Output ("set_Filename tok=0x{0:X8}  IL={1}" -f $sf.MetadataToken, (($sf.GetMethodBody().GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' '))
Write-Output ("get_Filename tok=0x{0:X8}  IL={1}" -f $gf.MetadataToken, (($gf.GetMethodBody().GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' '))
$want=@($sf.MetadataToken)
$types=@(); try{$types=$a.GetTypes()}catch{$types=@($_.Exception.Types|?{$_ -ne $null})}
foreach($ty in $types){
  $ms=@(); try{$ms=@($ty.GetMethods($bf))+@($ty.GetConstructors($bf))}catch{continue}
  foreach($m in $ms){
    $b=$null; try{$b=$m.GetMethodBody()}catch{}; if(-not $b){continue}
    $il=$b.GetILAsByteArray(); if(-not $il){continue}
    for($i=0;$i -lt $il.Length-4;$i++){
      if($il[$i+4] -ne 0x06){continue}
      $tok=$il[$i+1] -bor ($il[$i+2] -shl 8) -bor ($il[$i+3] -shl 16) -bor 0x06000000
      if($want -contains $tok){ Write-Output ("  SETTER CALLED IN: {0}.{1}" -f $ty.FullName,$m.Name) }
    }
  }
}
# also dump cq
$cq=$a.GetType('Extron.Configuration.Drivers.DriverFileAsset').GetMethod('cq',$bf)
Write-Output ("cq IL: " + (($cq.GetMethodBody().GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' '))
