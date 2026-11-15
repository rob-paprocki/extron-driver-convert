$ErrorActionPreference='Continue'
$dll='C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Drivers.dll'
$asm=[Reflection.Assembly]::LoadFrom($dll)
$mod=$asm.GetModules()[0]
foreach($t in @(0x0A000099,0x0A000089,0x0A0000EA,0x0A0000EB,0x0A0000ED,0x0A0000E0,0x0A0000E1)){
 try{$m=$mod.ResolveMember($t)
  $sig=''
  if($m -is [Reflection.MethodBase]){$sig='('+(($m.GetParameters()|%{$_.ParameterType.Name}) -join ', ')+')'; if($m -is [Reflection.MethodInfo]){$sig+=' -> '+$m.ReturnType.FullName}}
  Write-Output ("0x{0:X8}  {1} :: {2}{3}" -f $t,$m.DeclaringType.FullName,$m.Name,$sig)}
 catch{Write-Output ("0x{0:X8} ERR {1}" -f $t,$_.Exception.Message)}
}
Write-Output "---- embedded resources ----"
$asm.GetManifestResourceNames() | ForEach-Object { $s=$asm.GetManifestResourceStream($_); Write-Output ("{0}  len={1}" -f $_, $(if($s){$s.Length}else{'null'})) }
Write-Output "---- DriverAssetValidator members ----"
$bf=[Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
$ty=$asm.GetType('Extron.Configuration.Drivers.DriverAssetValidator')
$ty.GetConstructors($bf) | %{ $b=$_.GetMethodBody(); Write-Output (".ctor IL: " + (($b.GetILAsByteArray()|%{'{0:X2}' -f $_}) -join ' ')) }
$ty.GetFields($bf) | %{ Write-Output ("FIELD {0} {1}" -f $_.FieldType.Name,$_.Name) }
$en=$asm.GetType('Extron.Configuration.Drivers.DriverAssetValidator+ErrorCode')
[Enum]::GetNames($en) | %{ Write-Output ("ENUM {0} = {1}" -f $_, [int][Enum]::Parse($en,$_)) }
Write-Output "---- IResourceAsset ----"
$ca=[Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Contracts.dll')
foreach($n in @('Extron.Configuration.Contracts.Assets.IResourceAsset','Extron.Configuration.Contracts.Assets.IAsset','Extron.Configuration.Contracts.Assets.Drivers.IDriverFileAsset','Extron.Configuration.Contracts.Assets.Drivers.IDriverDescriptorAsset')){
 $it=$ca.GetType($n); if(-not $it){Write-Output "MISSING $n"; continue}
 Write-Output "INTERFACE $n : " + (($it.GetInterfaces()|%{$_.Name}) -join ', ')
 $it.GetMembers() | %{ Write-Output ("   {0} {1}" -f $_.MemberType,$_) }
}
