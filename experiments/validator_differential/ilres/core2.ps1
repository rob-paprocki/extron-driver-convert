$base='C:\Program Files (x86)\Extron\GCP\'
$a=[Reflection.Assembly]::LoadFrom($base+'Extron.Configuration.Core.dll')
$mod=$a.GetModules()[0]
foreach($t in @(0x06000974,0x0600097B,0x1B00018B)){
 try{$m=$mod.ResolveMember($t)
  $sig=''
  if($m -is [Reflection.MethodBase]){$sig='('+(($m.GetParameters()|%{$_.ParameterType.FullName}) -join ', ')+')'; if($m -is [Reflection.MethodInfo]){$sig+=' -> '+$m.ReturnType.FullName}}
  Write-Output ("0x{0:X8}  {1} :: {2}{3}" -f $t,$m.DeclaringType.FullName,$m.Name,$sig)
  if($m -is [Reflection.MethodBase]){$b=$m.GetMethodBody(); if($b){ Write-Output ("   IL: " + (($b.GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' ')); foreach($lv in $b.LocalVariables){Write-Output ("   local[{0}] {1}" -f $lv.LocalIndex,$lv.LocalType.FullName)} }}
 }catch{ try{$ty=$mod.ResolveType($t); Write-Output ("0x{0:X8}  TYPE {1}" -f $t,$ty.FullName)}catch{Write-Output ("0x{0:X8} ERR" -f $t)} }
}
