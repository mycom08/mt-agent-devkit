$ErrorActionPreference = 'Stop'
$interpreter = if ($env:MT_DEVKIT_PYTHON) { $env:MT_DEVKIT_PYTHON } else { 'python' }
& $interpreter -c 'import sys; assert sys.version_info >= (3,10)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ required; set MT_DEVKIT_PYTHON to its executable.' }
& $interpreter (Join-Path $PSScriptRoot 'lifecycle.py') @args
exit $LASTEXITCODE
