$p = Start-Process 'C:\Program Files (x86)\Extron\GCP\GCP.exe' -PassThru
Write-Output ("launched pid={0}" -f $p.Id)
for($i=0;$i -lt 90;$i++){
  Start-Sleep -Seconds 2
  $p.Refresh()
  if($p.HasExited){ Write-Output "EXITED early"; break }
  if($p.MainWindowTitle){ Write-Output ("window after {0}s: '{1}'" -f ($i*2), $p.MainWindowTitle); break }
}
$p.Refresh()
Write-Output ("final title: '{0}'  responding={1}" -f $p.MainWindowTitle, $p.Responding)
