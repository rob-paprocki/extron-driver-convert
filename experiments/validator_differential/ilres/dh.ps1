$a=[Reflection.Assembly]::LoadFrom('C:\Program Files (x86)\Extron\GCP\Extron.Configuration.Drivers.dll')
$s=$a.GetManifestResourceStream('Extron.Configuration.Drivers.Resources.ExtronDH.dat')
$ms=New-Object IO.MemoryStream
$s.CopyTo($ms)
$b=$ms.ToArray()
[IO.File]::WriteAllBytes('C:\Users\robp\AppData\Local\Temp\ilres\ExtronDH.dat',$b)
$txt=[Text.Encoding]::UTF8.GetString($b)
Write-Output ("len={0}" -f $b.Length)
Write-Output $txt.Substring(0,900)
$n=([regex]::Matches($txt,'<HashItem')).Count
Write-Output ("HashItem count = {0}" -f $n)
