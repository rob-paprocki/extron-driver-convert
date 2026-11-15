$ErrorActionPreference = 'Continue'
$dll = 'C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Drivers.dll'
$asm = [Reflection.Assembly]::LoadFrom($dll)
$mod = $asm.GetModules()[0]

$tokens = @(
 0x04000023,0x0400002A,0x0400002B,0x0400002C,0x0400002D,
 0x0A000060,0x0A00002E,0x0A000085,0x0A000086,0x0A00008B,0x0A000097,
 0x0A0000F3,0x0A0000F4,0x0A0000F5,0x0A0000F6,0x0A0000F7,0x0A0000F8,0x0A0000F9,0x0A0000FA,
 0x0A0000FB,0x0A0000FD,0x0A0000FE,0x0A0000FF,0x0A000100,
 0x2B00001B,0x2B000018,0x2B000019,0x2B00001A,
 0x1B000022,0x1B000028,0x01000022
)
foreach ($t in $tokens) {
  $s = ''
  try {
    $m = $mod.ResolveMember($t)
    $decl = if ($m.DeclaringType) { $m.DeclaringType.FullName } else { '<none>' }
    $sig = ''
    if ($m -is [Reflection.MethodBase]) {
      $sig = '(' + (($m.GetParameters() | ForEach-Object { $_.ParameterType.FullName }) -join ', ') + ')'
      if ($m -is [Reflection.MethodInfo]) { $sig = $sig + ' -> ' + $m.ReturnType.FullName }
      if ($m.IsGenericMethod) { $sig = $sig + ' [genargs: ' + (($m.GetGenericArguments() | ForEach-Object { $_.FullName }) -join ', ') + ']' }
    } elseif ($m -is [Reflection.FieldInfo]) {
      $sig = ' : ' + $m.FieldType.FullName
    }
    $s = "$decl :: $($m.Name)$sig"
  } catch {
    try { $ty = $mod.ResolveType($t); $s = "TYPE $($ty.FullName)" } catch { $s = "UNRESOLVED: $($_.Exception.Message)" }
  }
  Write-Output ("0x{0:X8}  {1}" -f $t, $s)
}

Write-Output "---- STRINGS ----"
foreach ($t in @(0x7000059A,0x70000602,0x70000644,0x70000650,0x7000065C,0x7000069C,0x7000069A,0x7000069E)) {
  try { Write-Output ("0x{0:X8}  `"{1}`"" -f $t, $mod.ResolveString($t)) }
  catch { Write-Output ("0x{0:X8}  UNRESOLVED {1}" -f $t, $_.Exception.Message) }
}
