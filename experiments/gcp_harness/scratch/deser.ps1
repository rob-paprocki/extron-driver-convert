$ErrorActionPreference='Continue'
$gcp='C:\Program Files (x86)\Extron\GCP'
Get-ChildItem "$gcp\Extron.Configuration.*.dll" | ForEach-Object {
  try { [Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null } catch {}
}
Add-Type -AssemblyName System.Runtime.Serialization.Formatters.Soap -ErrorAction SilentlyContinue
foreach($f in $args){
  Write-Output "=== $f"
  try{
    $fs=[IO.File]::OpenRead($f)
    $gz=New-Object IO.Compression.GZipStream($fs,[IO.Compression.CompressionMode]::Decompress)
    $ms=New-Object IO.MemoryStream
    $gz.CopyTo($ms); $gz.Dispose(); $fs.Dispose()
    $ms.Position=0
    Write-Output ("  decompressed: {0} bytes" -f $ms.Length)
    $bf=New-Object Runtime.Serialization.Formatters.Binary.BinaryFormatter
    $o=$bf.Deserialize($ms)
    Write-Output ("  OK: {0}" -f $o.GetType().FullName)
  } catch {
    $e=$_.Exception
    $d=0
    while($e -ne $null -and $d -lt 6){
      Write-Output ("  [{0}] {1}: {2}" -f $d,$e.GetType().FullName,$e.Message)
      $e=$e.InnerException; $d++
    }
  }
}
