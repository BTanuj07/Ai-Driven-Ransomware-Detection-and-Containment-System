# ARCS Authentication Diagnostic Script
Write-Host "=== ARCS Authentication Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if backend is running
Write-Host "[1/5] Checking Backend Status..." -ForegroundColor Yellow
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    if ($backend.StatusCode -eq 200) {
        Write-Host "  ✅ Backend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Backend is NOT running" -ForegroundColor Red
    Write-Host "  Action: Start backend with 'cd backend && python main.py'" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Test 2: Check if frontend is running
Write-Host "[2/5] Checking Frontend Status..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 5
    if ($frontend.StatusCode -eq 200) {
        Write-Host "  ✅ Frontend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Frontend is NOT running" -ForegroundColor Red
    Write-Host "  Action: Start frontend with 'cd frontend && npm run dev'" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Test 3: Check alerts endpoint (no auth required)
Write-Host "[3/5] Testing Alerts Endpoint (No Auth)..." -ForegroundColor Yellow
try {
    $alerts = Invoke-WebRequest -Uri "http://localhost:8000/api/alerts?limit=1" -UseBasicParsing -TimeoutSec 5
    if ($alerts.StatusCode -eq 200) {
        $alertData = $alerts.Content | ConvertFrom-Json
        $alertCount = $alertData.alerts.Count
        Write-Host "  ✅ Alerts endpoint working - Found $alertCount alert(s)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Alerts endpoint failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Check reports endpoint (requires auth)
Write-Host "[4/5] Testing Reports Endpoint (Requires Auth)..." -ForegroundColor Yellow
try {
    $reports = Invoke-WebRequest -Uri "http://localhost:8000/api/reports/summary" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ❌ Unexpected: Got response without auth" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "  ✅ Correctly requires authentication (401)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Test 5: Check Supabase configuration
Write-Host "[5/5] Checking Supabase Configuration..." -ForegroundColor Yellow
$envFile = "frontend/.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile
    $hasSupabaseUrl = $envContent | Select-String "VITE_SUPABASE_URL"
    $hasSupabaseKey = $envContent | Select-String "VITE_SUPABASE_ANON_KEY"
    
    if ($hasSupabaseUrl -and $hasSupabaseKey) {
        Write-Host "  ✅ Supabase configuration found" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Supabase configuration incomplete" -ForegroundColor Red
        Write-Host "  Missing: $(if (!$hasSupabaseUrl) { 'VITE_SUPABASE_URL ' })$(if (!$hasSupabaseKey) { 'VITE_SUPABASE_ANON_KEY' })" -ForegroundColor Gray
    }
} else {
    Write-Host "  ❌ frontend/.env file not found" -ForegroundColor Red
}
Write-Host ""

# Summary and recommendations
Write-Host "=== Diagnosis Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Common Issues & Solutions:" -ForegroundColor White
Write-Host ""
Write-Host "1. 401 Unauthorized Errors:" -ForegroundColor Yellow
Write-Host "   - Frontend not restarted after code changes" -ForegroundColor Gray
Write-Host "   - Solution: Stop frontend (Ctrl+C) and run 'npm run dev' again" -ForegroundColor Green
Write-Host ""
Write-Host "2. Supabase Session Not Available:" -ForegroundColor Yellow
Write-Host "   - User not logged in" -ForegroundColor Gray
Write-Host "   - Solution: Log out and log in again" -ForegroundColor Green
Write-Host ""
Write-Host "3. 500 Internal Server Errors:" -ForegroundColor Yellow
Write-Host "   - Backend database connection issues" -ForegroundColor Gray
Write-Host "   - Solution: Check backend terminal for error messages" -ForegroundColor Green
Write-Host ""
Write-Host "4. Reports Showing Zero:" -ForegroundColor Yellow
Write-Host "   - No data in MongoDB yet" -ForegroundColor Gray
Write-Host "   - Solution: Run simulation to generate alerts" -ForegroundColor Green
Write-Host "   - Command: python simulation/ransomware_simulator.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Restart Frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Clear Browser Cache:" -ForegroundColor White
Write-Host "   - Press Ctrl+Shift+R to hard refresh" -ForegroundColor Gray
Write-Host "   - Or clear cache in browser settings" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Log Out and Log In:" -ForegroundColor White
Write-Host "   - Click profile icon → Sign Out" -ForegroundColor Gray
Write-Host "   - Log in again with your credentials" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Check Browser Console:" -ForegroundColor White
Write-Host "   - Press F12 to open DevTools" -ForegroundColor Gray
Write-Host "   - Look for error messages" -ForegroundColor Gray
Write-Host "   - Check Network tab for failed requests" -ForegroundColor Gray
Write-Host ""
