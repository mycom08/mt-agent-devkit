$ErrorActionPreference = 'Stop'
& python (Join-Path $PSScriptRoot 'wait_work.py') @args
exit $LASTEXITCODE
