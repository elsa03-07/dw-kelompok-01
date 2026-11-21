# Demo Sprint 1 Automation Script
# ------------------------------------------------------------
# This PowerShell script automates the full reproducibility demo for
# the team project "dw‑kelompok‑01".  It performs the following steps
# in order:
#   1. Clone the repository to a temporary folder.
#   2. Download raw data for case 1.
#   3. Create a Python virtual‑environment.
#   4. Install all Python dependencies (including the required
#      pandera==0.20.0 version).
#   5. Run the data pipeline.
#   6. Verify that the generated Silver file matches the original
#      checksum.
#   7. (Optional) Record the whole session as a screen‑capture video
#      using FFmpeg.
# ------------------------------------------------------------

# -------------------- Configuration --------------------------
# Adjust these variables if you want to customize the paths.
$RepoUrl      = "https://github.com/elsa03-07/dw-kelompok-01.git"
$CloneRoot    = "$env:USERPROFILE\scratch"
$CloneDir     = Join-Path $CloneRoot "dw-kelompok-01-clone"
$VideoPath    = Join-Path $CloneRoot "demo-sprint-1-elsa.mp4"
$LogFile      = Join-Path $CloneRoot "demo-sprint-1.log"
$PanderaVer   = "0.20.0"
# ------------------------------------------------------------

# Helper function to write timestamps to the log file
function Write-Log { param([string]$msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] $msg" | Out-File -FilePath $LogFile -Append -Encoding utf8
    Write-Host $msg
}

# Start logging
"" > $LogFile   # clear previous log
Write-Log "=== Demo Sprint 1 started ==="

# 1. Clone the repository (Git must be in PATH)
if (Test-Path $CloneDir) {
    Write-Log "Removing existing clone directory..."
    Remove-Item -Recurse -Force $CloneDir
}
Write-Log "Cloning repository…"
git clone $RepoUrl $CloneDir 2>> $LogFile
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: git clone failed"; exit 1 }
Write-Log "Repository cloned to $CloneDir"

# Change to the cloned folder
Set-Location $CloneDir

# 2. Download raw data for case 1
Write-Log "Downloading raw data (case 1)…"
python unduh_data.py --kasus 1 >> $LogFile 2>&1
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: unduh_data.py failed"; exit 1 }
Write-Log "Data download completed"

# 3. Create virtual environment
Write-Log "Creating virtual environment…"
python -m venv .venv >> $LogFile 2>&1
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: venv creation failed"; exit 1 }

# 4. Activate venv and install dependencies
# NOTE: In PowerShell the activation script is .\venv\Scripts\Activate.ps1
Write-Log "Activating virtual environment…"
& "$CloneDir\.venv\Scripts\Activate.ps1"

Write-Log "Installing requirements from requirements.txt…"
python -m pip install -r requirements.txt >> $LogFile 2>&1
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: pip install requirements failed"; exit 1 }

# 5. Install the exact pandera version required by the repo
Write-Log "Installing pandera version $PanderaVer…"
python -m pip install "pandera==$PanderaVer" >> $LogFile 2>&1
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: pandera install failed"; exit 1 }

# 6. Run the pipeline
Write-Log "Running pipeline.py…"
python pipeline.py >> $LogFile 2>&1
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR: pipeline.py failed"; exit 1 }
Write-Log "Pipeline finished successfully"

# 7. Verify Silver checksum
$SilverPath = Join-Path $CloneDir "data\silver\silver.parquet"
if (Test-Path $SilverPath) {
    Write-Log "Computing SHA‑256 of Silver file…"
    $hash = Get-FileHash -Algorithm SHA256 $SilverPath
    Write-Log "SHA‑256 = $($hash.Hash)"
    # The reference hash from the original repo (case‑insensitive)
    $refHash = "9A57A26C239EC189632E1141A317334ABEDB94E30601F2A91AA0AEE79F951428"
    if ($hash.Hash.ToUpper() -eq $refHash) {
        Write-Log "✅ Checksum matches the committed Silver file"
    } else {
        Write-Log "⚠️ Checksum DIFFERENT from the committed file"
    }
} else {
    Write-Log "ERROR: Silver file not found at $SilverPath"
    exit 1
}

# 8. (Optional) Record screen with FFmpeg
# -----------------------------------------------------------------
# FFmpeg can capture the whole monitor or a region.  The command below
# records the primary display at 30 fps for up to 600 seconds (10 min).
# Adjust "-t" (duration) and "-video_size" / "-i desktop" as needed.
# Make sure ffmpeg.exe is in PATH (or give the full path).
# -----------------------------------------------------------------
$record = $false   # set to $true to enable recording
if ($record) {
    Write-Log "Starting screen capture (FFmpeg)…"
    $ffmpegCmd = @(
        "ffmpeg",
        "-y",                # overwrite output file
        "-f", "gdigrab",    # Windows desktop capture
        "-framerate", "30",
        "-i", "desktop",
        "-t", "600",        # max 10 minutes
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        $VideoPath
    )
    & $ffmpegCmd 2>> $LogFile
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Screen capture saved to $VideoPath"
    } else {
        Write-Log "ERROR: FFmpeg recording failed"
    }
} else {
    Write-Log "Screen recording skipped (set `$record = `$true to enable)"
}

Write-Log "=== Demo Sprint 1 completed ==="

# End of script
