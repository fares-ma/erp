param(
    [int]$Port = $(if ($env:ERPNEXT_PORT) { [int]$env:ERPNEXT_PORT } else { 8080 }),
    [switch]$SeedDemo,
    [switch]$SeedFactory,
    [switch]$SeedAll
)

$ErrorActionPreference = "Stop"

function Test-DockerDaemon {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $null = & docker info 2>&1
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $prev
    }
}

# Locate docker CLI
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    $dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
    if (Test-Path (Join-Path $dockerBin "docker.exe")) {
        $env:PATH = "$dockerBin;$env:PATH"
        $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    }
}

if (-not $dockerCmd) {
    Write-Error "Docker CLI (docker.exe) was not found. Please install Docker Desktop and try again."
    exit 1
}

# Check if Docker daemon is running; start Docker Desktop if needed
if (-not (Test-DockerDaemon)) {
    $dockerDesktopExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path $dockerDesktopExe)) {
        Write-Error "Docker daemon is not running and '$dockerDesktopExe' was not found. Please start Docker Desktop manually."
        exit 1
    }

    Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
    Start-Process -FilePath $dockerDesktopExe

    $maxWaitSeconds = 180
    $elapsed = 0
    while ($elapsed -lt $maxWaitSeconds) {
        Start-Sleep -Seconds 5
        $elapsed += 5
        if (Test-DockerDaemon) {
            break
        }
        Write-Host "Waiting for Docker daemon ($elapsed/${maxWaitSeconds}s)..." -ForegroundColor DarkGray
    }

    if (-not (Test-DockerDaemon)) {
        Write-Host ""
        Write-Warning "Docker daemon did not respond within $maxWaitSeconds seconds."
        Write-Host "Please open Docker Desktop, accept any first-run prompts (and restart Windows if WSL2 requires it), then re-run .\start-erpnext.ps1" -ForegroundColor Yellow
        exit 1
    }
}

$composeDir = Join-Path $PSScriptRoot "frappe_docker"
$composeFile = Join-Path $composeDir "pwd.yml"
if (-not (Test-Path $composeFile)) {
    Write-Error "Could not find '$composeFile'."
    exit 1
}

$env:ERPNEXT_PORT = "$Port"

function Invoke-SeedScript {
    param([string]$ScriptName)
    $hostScript = Join-Path $PSScriptRoot $ScriptName
    if (-not (Test-Path $hostScript)) {
        Write-Error "Seed script '$hostScript' was not found."
        exit 1
    }
    Write-Host ""
    Write-Host "Running seed script: $ScriptName ..." -ForegroundColor Cyan
    & docker compose -f pwd.yml cp $hostScript "backend:/tmp/$ScriptName"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to copy '$ScriptName' into backend container (exit $LASTEXITCODE)."
        exit $LASTEXITCODE
    }
    & docker compose -f pwd.yml exec -T backend /home/frappe/frappe-bench/env/bin/python "/tmp/$ScriptName"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Seed script '$ScriptName' failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
}

Push-Location $composeDir
$prevErrPref = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $images = @("redis:6.2-alpine", "mariadb:11.8", "frappe/erpnext:v16.60.0")
    foreach ($img in $images) {
        $null = & docker image inspect $img 2>&1
        if ($LASTEXITCODE -ne 0) {
            $pulled = $false
            for ($attempt = 1; $attempt -le 10; $attempt++) {
                Write-Host "Pulling $img (attempt $attempt/10) ..." -ForegroundColor Cyan
                & docker pull $img
                if ($LASTEXITCODE -eq 0) {
                    $pulled = $true
                    break
                }
                Write-Warning "docker pull $img failed (exit $LASTEXITCODE). Retrying in 10s..."
                Start-Sleep -Seconds 10
            }
            if (-not $pulled) {
                Write-Error "docker pull $img failed after 10 attempts."
                exit 1
            }
        }
    }

    Write-Host "Starting ERPNext containers via docker compose -f pwd.yml up -d --pull never (port $Port) ..." -ForegroundColor Cyan
    & docker compose -f pwd.yml up -d --pull never
    if ($LASTEXITCODE -ne 0) {
        Write-Error "docker compose up failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }

    Write-Host ""
    Write-Host "Current container status:" -ForegroundColor Cyan
    & docker compose -f pwd.yml ps

    Write-Host ""
    Write-Host "Waiting for ERPNext site setup (create-site)..." -ForegroundColor Cyan
    & docker compose -f pwd.yml logs -f create-site

    $pingUrl = "http://localhost:$Port/api/method/ping"
    Write-Host ""
    Write-Host "Verifying $pingUrl ..." -ForegroundColor Cyan
    $pingOk = $false
    for ($p = 1; $p -le 18; $p++) {
        try {
            $resp = Invoke-WebRequest -Uri $pingUrl -UseBasicParsing -TimeoutSec 15
            if ($resp.StatusCode -eq 200) {
                Write-Host "ERPNext is LIVE! Response: $($resp.Content)" -ForegroundColor Green
                $pingOk = $true
                break
            }
        }
        catch {
            Write-Host "Waiting for web server ($p/18)..." -ForegroundColor DarkGray
            Start-Sleep -Seconds 5
        }
    }
    if (-not $pingOk) {
        Write-Warning "Containers are up, but $pingUrl did not return 200 yet. Check 'docker compose -f pwd.yml ps -a'."
    }

    if ($SeedAll) {
        Invoke-SeedScript "seed_demo_data.py"
        Invoke-SeedScript "seed_appliance_factory.py"
        Invoke-SeedScript "seed_factory_users_and_extras.py"
    }
    else {
        if ($SeedDemo) {
            Invoke-SeedScript "seed_demo_data.py"
        }
        if ($SeedFactory) {
            Invoke-SeedScript "seed_appliance_factory.py"
            Invoke-SeedScript "seed_factory_users_and_extras.py"
        }
    }
}
finally {
    $ErrorActionPreference = $prevErrPref
    Pop-Location
}

Write-Host ""
Write-Host "Digitbox Manufacturing ERP is ready!" -ForegroundColor Green
Write-Host "  - First-time site creation (create-site) takes about 2-5 minutes."
Write-Host "  - Watch progress: cd `"$composeDir`"; docker compose -f pwd.yml logs -f create-site"
Write-Host "  - URL:         http://localhost:$Port"
Write-Host "  - Site:        frontend"
Write-Host "  - Username:    Administrator"
Write-Host "  - Password:    admin"
if ($SeedAll -or $SeedFactory) {
    Write-Host "  - Factory Demo Users (Password: Factory@2026):"
    Write-Host "      gm@factory.local | stock@factory.local | production@factory.local"
    Write-Host "      qc@factory.local | accounts@factory.local"
}
