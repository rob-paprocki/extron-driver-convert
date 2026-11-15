$ErrorActionPreference='Continue'
$base='C:\Program Files (x86)\Extron\GCP\'
[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll') | Out-Null
foreach($f in @('GCP.exe','Extron.Configuration.GCPro.dll')){
  Write-Output "=== $f ==="
  try{ $a=[Reflection.Assembly]::LoadFrom($base+$f) }catch{ Write-Output "  LOAD FAIL"; continue }
  $mod=$a.GetModules()[0]
  # brute-force MemberRef table for members declared on DriverAssetValidator
  $want=@{}
  $miss=0
  for($i=1;$i -lt 20000;$i++){
    $tok=0x0A000000 -bor $i
    try{ $r=$mod.ResolveMember($tok); $miss=0 }catch{ $miss++; if($miss -gt 300){break}; continue }
    if($r.DeclaringType -and $r.DeclaringType.Name -eq 'DriverAssetValidator'){
      $want[$tok]=$r.Name
      Write-Output ("  MEMBERREF 0x{0:X8} -> {1}.{2}" -f $tok,$r.DeclaringType.FullName,$r.Name)
    }
  }
  if($want.Count -eq 0){ Write-Output "  (no DriverAssetValidator memberrefs found)"; continue }
  $bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
  $types=@(); try{$types=$a.GetTypes()}catch{ $ex=$_.Exception; while($ex.InnerException -and -not ($ex -is [Reflection.ReflectionTypeLoadException])){$ex=$ex.InnerException}; $types=@($ex.Types|?{$_ -ne $null}) }
  foreach($ty in $types){
    $ms=@(); try{$ms=@($ty.GetMethods($bf))+@($ty.GetConstructors($bf))}catch{continue}
    foreach($m in $ms){
      $b=$null; try{$b=$m.GetMethodBody()}catch{}
      if(-not $b){continue}
      $il=$null; try{$il=$b.GetILAsByteArray()}catch{}
      if(-not $il){continue}
      for($i=0;$i -lt $il.Length-4;$i++){
        if($il[$i+4] -ne 0x0A){continue}
        $tok = $il[$i+1] -bor ($il[$i+2] -shl 8) -bor ($il[$i+3] -shl 16) -bor 0x0A000000
        if($want.ContainsKey($tok)){ Write-Output ("  USE: {0}.{1}  ->  {2}  (opcode 0x{3:X2})" -f $ty.FullName,$m.Name,$want[$tok],$il[$i]) }
      }
    }
  }
}
