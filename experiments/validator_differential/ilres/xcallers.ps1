$ErrorActionPreference='Continue'
$base='C:\Program Files (x86)\Extron\GCP\'
[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll') | Out-Null
foreach($f in @('GCP.exe','Extron.Configuration.GCPro.dll')){
  Write-Output "=== $f ==="
  try{ $a=[Reflection.Assembly]::LoadFrom($base+$f) }catch{ Write-Output "  LOAD FAIL: $($_.Exception.Message)"; continue }
  $mod=$a.GetModules()[0]
  $types=@(); try{$types=$a.GetTypes()}catch{ $ex=$_.Exception; while($ex.InnerException -and -not ($ex -is [Reflection.ReflectionTypeLoadException])){$ex=$ex.InnerException}; if($ex -is [Reflection.ReflectionTypeLoadException]){$types=@($ex.Types | Where-Object {$_ -ne $null})} else {Write-Output "  GetTypes failed: $($ex.GetType().Name) $($ex.Message)"} }
  Write-Output ("  types loaded: {0}" -f $types.Count)
  $bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
  foreach($ty in $types){
    $ms=@(); try{$ms=@($ty.GetMethods($bf))+@($ty.GetConstructors($bf))}catch{continue}
    foreach($m in $ms){
      $b=$null; try{$b=$m.GetMethodBody()}catch{}
      if(-not $b){continue}
      $il=$null; try{$il=$b.GetILAsByteArray()}catch{}
      if(-not $il){continue}
      for($i=0;$i -lt $il.Length-4;$i++){
        if(($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) -and $il[$i+4] -eq 0x0A){
          $tok = $il[$i+1] -bor ($il[$i+2] -shl 8) -bor ($il[$i+3] -shl 16) -bor (0x0A -shl 24)
          try{ $r=$mod.ResolveMember($tok) }catch{ continue }
          if($r.DeclaringType -and $r.DeclaringType.Name -eq 'DriverAssetValidator'){
            Write-Output ("  {0}.{1}  calls  {2}" -f $ty.FullName,$m.Name,$r.Name)
          }
        }
      }
    }
  }
}
