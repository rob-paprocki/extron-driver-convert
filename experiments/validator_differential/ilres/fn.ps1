$ErrorActionPreference='Continue'
$base='C:\Program Files (x86)\Extron\GCP\'
$drv=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll')
$bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
$types=@(); try{$types=$drv.GetTypes()}catch{$types=@($_.Exception.Types|?{$_ -ne $null})}
foreach($ty in $types){
  if($ty.FullName -notmatch 'DriverFileAsset'){continue}
  Write-Output "=== $($ty.FullName)  base=$($ty.BaseType)"
  foreach($m in ($ty.GetMethods($bf))){
    if($m.Name -notmatch 'Filename|Load|Unload|Manifest|ResourceHash'){continue}
    Write-Output ("  {0} {1}({2})  tok=0x{3:X8}" -f $m.ReturnType.Name,$m.Name,(($m.GetParameters()|%{$_.ParameterType.Name}) -join ','),$m.MetadataToken)
    $b=$m.GetMethodBody(); if($b){ Write-Output ("    IL: " + (($b.GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' ')) }
  }
}
