# PowerShell script to copy Module 3 code to Module 4/src
# Run this from your jhu_software_concepts directory

Write-Host "Copying Module 3 code to Module 4/src..." -ForegroundColor Cyan
Write-Host ""

# Copy load_data.py
if (Test-Path "module_3/load_data.py") {
    Copy-Item -Path "module_3/load_data.py" -Destination "module_4/src/load_data.py" -Force
    Write-Host "Copied load_data.py" -ForegroundColor Green
}

# Copy query_data.py
if (Test-Path "module_3/query_data.py") {
    Copy-Item -Path "module_3/query_data.py" -Destination "module_4/src/query_data.py" -Force
    Write-Host "Copied query_data.py" -ForegroundColor Green
}

# Copy run.py
if (Test-Path "module_3/run.py") {
    Copy-Item -Path "module_3/run.py" -Destination "module_4/src/run.py" -Force
    Write-Host "Copied run.py" -ForegroundColor Green
}

# Copy app directory
if (Test-Path "module_3/app") {
    if (Test-Path "module_4/src/app") {
        Remove-Item -Path "module_4/src/app" -Recurse -Force
    }
    Copy-Item -Path "module_3/app" -Destination "module_4/src/app" -Recurse -Force
    Write-Host "Copied app/ directory" -ForegroundColor Green
}

# Copy module_2.1 directory (scrape.py, clean.py, etc.)
if (Test-Path "module_3/module_2.1") {
    if (-not (Test-Path "module_4/src/module_2.1")) {
        New-Item -ItemType Directory -Path "module_4/src/module_2.1" | Out-Null
    }
    
    # Copy scrape.py
    if (Test-Path "module_3/module_2.1/scrape.py") {
        Copy-Item -Path "module_3/module_2.1/scrape.py" -Destination "module_4/src/module_2.1/scrape.py" -Force
        Write-Host "Copied scrape.py" -ForegroundColor Green
    }
    
    # Copy clean.py
    if (Test-Path "module_3/module_2.1/clean.py") {
        Copy-Item -Path "module_3/module_2.1/clean.py" -Destination "module_4/src/module_2.1/clean.py" -Force
        Write-Host "Copied clean.py" -ForegroundColor Green
    }
    
    # Copy llm_hosting directory (optional - contains model files)
    if (Test-Path "module_3/module_2.1/llm_hosting") {
        Copy-Item -Path "module_3/module_2.1/llm_hosting" -Destination "module_4/src/module_2.1/llm_hosting" -Recurse -Force
        Write-Host "Copied llm_hosting/ directory" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Code copy complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Files copied to module_4/src/" -ForegroundColor Cyan
Write-Host ""
