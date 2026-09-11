$ErrorActionPreference='Continue'
$gcp='C:\Program Files (x86)\Extron\GCP'
$loaded=@{}
Get-ChildItem "$gcp\*.dll" | ForEach-Object {
  try { $a=[Reflection.Assembly]::LoadFrom($_.FullName); $loaded[$a.GetName().Name]=$a } catch {}
}
Write-Output ("loaded {0} assemblies" -f $loaded.Count)
$handler = [ResolveEventHandler]{
  param($sender,$e)
  $simple = $e.Name.Split(',')[0]
  if($script:loaded.ContainsKey($simple)){ return $script:loaded[$simple] }
  return $null
}
[AppDomain]::CurrentDomain.add_AssemblyResolve($handler)
foreach($f in $args){
  Write-Output "=== $(Split-Path $f -Leaf)"
  try{
    $fs=[IO.File]::OpenRead($f)
    $gz=New-Object IO.Compression.GZipStream($fs,[IO.Compression.CompressionMode]::Decompress)
    $ms=New-Object IO.MemoryStream
    $gz.CopyTo($ms); $gz.Dispose(); $fs.Dispose(); $ms.Position=0
    $bf=New-Object Runtime.Serialization.Formatters.Binary.BinaryFormatter
    $o=$bf.Deserialize($ms)
    Write-Output ("  OK: {0}" -f $o.GetType().FullName)
  } catch {
    $e=$_.Exception; $d=0
    while($e -ne $null -and $d -lt 6){
      Write-Output ("  [{0}] {1}" -f $d,$e.GetType().FullName)
      Write-Output ("      {0}" -f $e.Message)
      $e=$e.InnerException; $d++
    }
  }
}
