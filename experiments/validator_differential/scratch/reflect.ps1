$ErrorActionPreference='Stop'
$dir='C:\Program Files (x86)\Extron\GCP'
[System.AppDomain]::CurrentDomain.add_AssemblyResolve({
  param($s,$e)
  $n=(New-Object System.Reflection.AssemblyName($e.Name)).Name
  $p=Join-Path $dir ($n + '.dll')
  if (Test-Path $p) { return [System.Reflection.Assembly]::LoadFrom($p) }
  return $null
})
$asm=[System.Reflection.Assembly]::LoadFrom((Join-Path $dir 'Extron.Configuration.Drivers.dll'))
Write-Output ("ASM: " + $asm.FullName)
$t=$asm.GetType('Extron.Configuration.Drivers.DriverAssetValidator')
Write-Output ("TYPE: " + $t.FullName + " abstract=" + $t.IsAbstract + " sealed=" + $t.IsSealed)
foreach($m in $t.GetMethods('Public,NonPublic,Instance,Static,DeclaredOnly')){
  $ps = ($m.GetParameters() | ForEach-Object { $_.ParameterType.Name + ' ' + $_.Name }) -join ', '
  Write-Output ("  M: " + $m.ReturnType.Name + " " + $m.Name + "(" + $ps + ") static=" + $m.IsStatic + " public=" + $m.IsPublic)
}
foreach($f in $t.GetFields('Public,NonPublic,Instance,Static,DeclaredOnly')){
  Write-Output ("  F: " + $f.FieldType.Name + " " + $f.Name + " static=" + $f.IsStatic)
}
foreach($c in $t.GetConstructors('Public,NonPublic,Instance,DeclaredOnly')){
  $ps = ($c.GetParameters() | ForEach-Object { $_.ParameterType.Name }) -join ', '
  Write-Output ("  C: .ctor(" + $ps + ")")
}
$e=$asm.GetType('Extron.Configuration.Drivers.DriverAssetValidator+ErrorCode')
if($e){ foreach($n in [Enum]::GetNames($e)){ Write-Output ("  E: " + $n + " = " + [int][Enum]::Parse($e,$n)) } }
