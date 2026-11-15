$ErrorActionPreference = 'Stop'
$dll = 'C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Drivers.dll'
$asm = [Reflection.Assembly]::LoadFrom($dll)
Write-Output "ASM: $($asm.FullName)"
$t = $asm.GetTypes() | Where-Object { $_.FullName -like '*DriverAssetValidator*' }
foreach ($ty in $t) { Write-Output "TYPE: $($ty.FullName)" }
$ty = $t[0]
$bf = [Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
foreach ($m in $ty.GetMethods($bf)) {
  $ps = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.FullName) $($_.Name)" }) -join ', '
  Write-Output ("METHOD: static={0} {1} {2}({3})  token=0x{4:X8}" -f $m.IsStatic, $m.ReturnType.FullName, $m.Name, $ps, $m.MetadataToken)
  $b = $m.GetMethodBody()
  if ($b) {
    Write-Output ("  maxstack={0} initlocals={1} ilsize={2}" -f $b.MaxStackSize, $b.InitLocals, $b.GetILAsByteArray().Length)
    foreach ($lv in $b.LocalVariables) { Write-Output ("  local[{0}] {1}" -f $lv.LocalIndex, $lv.LocalType.FullName) }
    foreach ($eh in $b.ExceptionHandlingClauses) {
      Write-Output ("  EH: {0} try[0x{1:X4}..0x{2:X4}) handler[0x{3:X4}..0x{4:X4})" -f $eh.Flags, $eh.TryOffset, ($eh.TryOffset+$eh.TryLength), $eh.HandlerOffset, ($eh.HandlerOffset+$eh.HandlerLength))
    }
    $hex = ($b.GetILAsByteArray() | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
    Write-Output "  IL: $hex"
  }
}
