$ErrorActionPreference='Continue'
$gcp='C:\Program Files (x86)\Extron\GCP'
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll") | Out-Null
$t=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll").GetType('Extron.Configuration.Drivers.DriverFileAsset')
$m=$t.GetMethods([Reflection.BindingFlags]'Public,Static,NonPublic') | Where-Object { $_.Name -like '*LoadFrom*' }
foreach($x in $m){ Write-Output ("METHOD {0}({1})" -f $x.Name, (($x.GetParameters()|%{$_.ParameterType.Name+' '+$_.Name}) -join ', ')) }
foreach($f in $args){
  Write-Output "=== $f"
  try{
    $r=$t::LoadFromFile($f)
    if($r -eq $null){ Write-Output "  RESULT: null" }
    else { Write-Output ("  RESULT: {0}  name={1}" -f $r.GetType().Name, $r.Name) }
  } catch {
    $e=$_.Exception; while($e.InnerException){$e=$e.InnerException}
    Write-Output ("  THREW: {0}: {1}" -f $e.GetType().FullName, $e.Message)
  }
}
