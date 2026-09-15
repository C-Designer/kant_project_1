# Run from Windows PowerShell 5.1+ or PowerShell 7.
# No execution-policy changes, git writes, cloud calls, or automatic model downloads.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-z0-9][a-z0-9_-]{0,63}$')][string]$Participant,
    [Parameter(Mandatory = $true)][string]$Model,
    [string]$DeviceLabel = 'not-recorded',
    [string]$RunId = '',
    [string]$ModelCardUrl = '',
    [string]$LicenseUrl = '',
    [ValidateRange(1, 2147483647)][int]$NumCtx = 8192,
    [ValidateRange(1, 2147483647)][int]$NumPredict = 2048,
    [ValidateRange(0.0, 2.0)][double]$Temperature = 0.2,
    [int]$Seed = 42
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Program failed with exit code $LASTEXITCODE. Stop and inspect the output; no git push was performed."
    }
}

if ($Participant -match '^(con|prn|aux|nul|com[1-9]|lpt[1-9])$') {
    throw 'Participant is a Windows reserved name.'
}
$LastModelPart = ($Model -split '/')[-1]
if ($LastModelPart -notmatch '^[^:]+:.+$' -or $Model.StartsWith('-') -or $Model -match '\s') {
    throw 'Use the full Ollama model tag, for example MODEL:FULL-TAG.'
}
if ([string]::IsNullOrEmpty($RunId)) {
    $RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ', [System.Globalization.CultureInfo]::InvariantCulture).ToLowerInvariant() + '-' + ([guid]::NewGuid().ToString('N').Substring(0, 8))
}
if ($RunId -cnotmatch '^[a-z0-9][a-z0-9_-]{0,63}$' -or $RunId -match '^(con|prn|aux|nul|com[1-9]|lpt[1-9])$') {
    throw 'RunId must be a safe lowercase ID of 1-64 characters; no path separators or reserved names.'
}
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunDir = "results/$Participant/$RunId"
$VerifyDir = "runs/verify-$Participant-$RunId"
$OriginalLocation = Get-Location
try {
    Set-Location $RepoRoot
    if ((Test-Path -LiteralPath $RunDir) -or (Test-Path -LiteralPath $VerifyDir)) {
        throw 'Output already exists. Use a new RunId; previous results will not be overwritten.'
    }
    $null = Get-Command uv -ErrorAction Stop
    $null = Get-Command docker -ErrorAction Stop
    Invoke-Checked 'uv' @('sync', '--frozen')
    Invoke-Checked 'docker' @('build', '-t', 'kant-harness:1', '.')
    Invoke-Checked 'uv' @('run', 'python', '-m', 'harness', 'verify-cases', '--out', $VerifyDir)
    $Verification = Get-Content -LiteralPath "$VerifyDir/verification_summary.json" -Raw | ConvertFrom-Json
    if ($Verification.all_valid -ne $true) {
        throw 'Reference/starter verification did not pass. Do not start the model experiment.'
    }
    $RunnerArgs = @('run', 'python', '-m', 'harness', 'run-model', '--participant', $Participant,
        '--model', $Model, '--run-id', $RunId, '--device-label', $DeviceLabel,
        '--num-ctx', $NumCtx.ToString(), '--num-predict', $NumPredict.ToString(),
        '--temperature', $Temperature.ToString([System.Globalization.CultureInfo]::InvariantCulture), '--seed', $Seed.ToString())
    if ($ModelCardUrl) { $RunnerArgs += @('--model-card-url', $ModelCardUrl) }
    if ($LicenseUrl) { $RunnerArgs += @('--license-url', $LicenseUrl) }
    Invoke-Checked 'uv' $RunnerArgs
    Write-Host ""
    Write-Host "Results: $RunDir"
    Write-Host 'Review REPORT.md (including failures/incomplete warnings), fill NOTES.md, and inspect logs for sensitive information.'
    Write-Host 'The script has NOT committed or pushed anything.'
    Write-Host "Repository root: $RepoRoot"
    Write-Host 'Return to the repository root and follow docs/INDIVIDUAL_RUN.md section 5.'
    Write-Host 'That guide checks the main branch, staged-file scope and every git exit code before push.'
}
finally {
    Set-Location $OriginalLocation
}
