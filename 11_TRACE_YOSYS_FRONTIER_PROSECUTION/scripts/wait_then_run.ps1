# wait until a results CSV has N data rows, then run a trace_batch job list (sequencing without oversubscribing CPUs)
param([string]$WaitCsv, [int]$Rows, [string]$Jobs, [string]$Out, [int]$Par = 3)
Set-Location (Join-Path $PSScriptRoot '..')
while ($true) {
  $n = 0
  if (Test-Path $WaitCsv) { $n = (Get-Content $WaitCsv | Measure-Object -Line).Lines - 1 }
  if ($n -ge $Rows) { break }
  Start-Sleep -Seconds 10
}
python scripts\trace_batch.py $Jobs $Out $Par
