$ErrorActionPreference='Continue'
$dll='C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Drivers.dll'
$asm=[Reflection.Assembly]::LoadFrom($dll)
$targets=@{ '0x06000098'='ComputeHash'; '0x06000090'='LoadDefaultFromResource'; '0x06000099'='Validate'; '0x06000093'='Load(string)'; '0x06000094'='Load(stream)'; '0x06000095'='ProcessDriverDirectory' }
$bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
foreach($ty in $asm.GetTypes()){
  foreach($m in ($ty.GetMethods($bf) + $ty.GetConstructors($bf))){
    $b=$null; try{$b=$m.GetMethodBody()}catch{}
    if(-not $b){continue}
    $il=$b.GetILAsByteArray()
    for($i=0;$i -lt $il.Length-4;$i++){
      if(($il[$i] -eq 0x28 -or $il[$i] -eq 0x6F) -and $il[$i+4] -eq 0x06){
        $tok = $il[$i+1] -bor ($il[$i+2] -shl 8) -bor ($il[$i+3] -shl 16) -bor (0x06 -shl 24)
        $k = '0x{0:X8}' -f $tok
        if($targets.ContainsKey($k)){ Write-Output ("CALLER of {0} : {1}.{2}" -f $targets[$k], $ty.FullName, $m.Name) }
      }
    }
  }
}
