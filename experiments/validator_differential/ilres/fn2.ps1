$base='C:\Program Files (x86)\Extron\GCP\'
$a=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll')
$mod=$a.GetModules()[0]
foreach($t in @(0x0A0000A1,0x0A0000A2,0x0A000044,0x0A0000BF,0x0A000095,0x06000061,0x06000062,0x06000063)){
 try{$m=$mod.ResolveMember($t)
  $sig=''
  if($m -is [Reflection.MethodBase]){$sig='('+(($m.GetParameters()|%{$_.ParameterType.Name}) -join ', ')+')'; if($m -is [Reflection.MethodInfo]){$sig+=' -> '+$m.ReturnType.Name}}
  Write-Output ("0x{0:X8}  {1} :: {2}{3}" -f $t,$m.DeclaringType.FullName,$m.Name,$sig)}
 catch{Write-Output ("0x{0:X8} ERR" -f $t)}
}
foreach($t in @(0x70000349,0x70000353,0x7000035F,0x7000032B)){
 try{Write-Output ("0x{0:X8}  `"{1}`"" -f $t,$mod.ResolveString($t))}catch{Write-Output ("0x{0:X8} ERR" -f $t)}
}
