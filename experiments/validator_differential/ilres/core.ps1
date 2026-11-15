$ErrorActionPreference='Continue'
$base='C:\Program Files (x86)\Extron\GCP\'
Get-ChildItem $base -Filter 'Extron.Configuration.Core*.dll' | ForEach-Object { Write-Output $_.Name }
$a=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Core.dll')
$mod=$a.GetModules()[0]
$bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
foreach($n in @('Extron.Configuration.Core.Assets.Resource.StreamResourceAsset','Extron.Configuration.Core.Assets.Resource.ResourceAssetBase')){
  $ty=$a.GetType($n); if(-not $ty){Write-Output "MISSING $n"; continue}
  Write-Output "=== $n (base $($ty.BaseType))"
  foreach($m in $ty.GetMethods($bf)){
    if($m.Name -notmatch 'HashCode|Content|Save|Load'){continue}
    Write-Output ("  {0} {1}({2})" -f $m.ReturnType.Name,$m.Name, (($m.GetParameters()|%{$_.ParameterType.Name}) -join ','))
    $b=$m.GetMethodBody(); if($b){
      Write-Output ("    IL: " + (($b.GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' '))
      foreach($lv in $b.LocalVariables){Write-Output ("    local[{0}] {1}" -f $lv.LocalIndex,$lv.LocalType.FullName)}
    }
  }
}
