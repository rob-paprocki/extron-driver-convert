$base='C:\Program Files (x86)\Extron\GCP\'
$a=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Drivers.dll')
$mod=$a.GetModules()[0]
foreach($t in @(0x0A0000A3,0x0A0000A4,0x0A0000A5,0x0A0000A6,0x0A0000A7,0x0A0000A8,0x0A0000A9,0x0A0000AA,0x0A0000AB,0x0A000052)){
 try{$m=$mod.ResolveMember($t)
  $sig=''
  if($m -is [Reflection.MethodBase]){$sig='('+(($m.GetParameters()|%{$_.ParameterType.Name}) -join ', ')+')'; if($m -is [Reflection.MethodInfo]){$sig+=' -> '+$m.ReturnType.Name}}
  Write-Output ("0x{0:X8}  {1} :: {2}{3}" -f $t,$m.DeclaringType.FullName,$m.Name,$sig)}
 catch{Write-Output ("0x{0:X8} ERR" -f $t)}
}
