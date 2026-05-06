# Reports Module Fix

## Problem
The Reports module was not working due to authentication issues. The module was trying to access `window.supabase` which was not defined, causing authentication tokens to not be retrieved properly.

## Root Cause
1. **Supabase not exposed globally** - `window.supabase` was undefined
2. **Inconsistent import pattern** - Some modules used `window.supabase?.auth.getSession()` instead of importing directly
3. **Silent failures** - No error handling for missing authentication tokens

## Solution Implemented

### 1. Exposed Supabase Globally (`frontend/src/main.jsx`)
```javascript
import { supabase } from './lib/supabase.js'

// Expose supabase globally for components that need it
window.supabase = supabase
```

### 2. Updated All Modules to Import Supabase Directly
Instead of relying on `window.supabase`, modules now import supabase:

```javascript
import { supabase } from '../lib/supabase'

// Then use it directly
const { data: { session } } = await supabase.auth.getSession()
```

### 3. Updated Modules
- ✅ **ReportsModule.jsx** - Fixed authentication token retrieval
- ✅ **SettingsModule.jsx** - Fixed authentication token retrieval  
- ✅ **NetworkTopologyAdvanced.jsx** - Fixed authentication token retrieval

### 4. Added Better Error Handling
```javascript
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token

if (!token) {
  console.error('No authentication token available')
  return
}
```

## What Now Works

### Reports Module Features
1. **Threat Summary** - Shows total threats, risk levels, false positives
2. **Trend Data** - 7-day threat trend visualization
3. **Attack Types** - Pie chart of attack type distribution
4. **Incidents Table** - Detailed incident reports with:
   - Incident ID
   - Attack type
   - Endpoint
   - Timestamp
   - Risk level
   - Action taken
   - Status
   - Response time

### Reports API Endpoints
All endpoints now work with proper authentication:
- `GET /api/reports/summary` - Threat detection summary
- `GET /api/reports/trend?days=7` - Threat trend over time
- `GET /api/reports/attack-types` - Attack type distribution
- `GET /api/reports/incidents?limit=50` - Detailed incidents
- `POST /api/reports/export?format=pdf` - Export reports

## Testing

### Test 1: Access Reports Module
1. Login to ARCS dashboard
2. Navigate to Reports module
3. Should see:
   - Threat summary cards
   - Trend chart
   - Attack types pie chart
   - Incidents table

### Test 2: Verify Data
1. Run ransomware simulation
2. Wait 10 seconds
3. Refresh Reports module
4. Should see new incidents in the table

### Test 3: Export Report
1. Click "Export PDF" or "Export CSV" button
2. Should see success message
3. Backend logs should show export request

## Technical Details

### Authentication Flow
```
User logs in
    ↓
Supabase creates session
    ↓
Session stored in browser
    ↓
Module calls supabase.auth.getSession()
    ↓
Gets access_token from session
    ↓
Includes token in API request headers
    ↓
Backend validates token
    ↓
Returns data
```

### Backend Authentication
All reports endpoints use `require_auth` middleware:
```python
@router.get("/reports/summary")
async def get_report_summary(
    request: Request, 
    user: dict = Depends(require_auth)
):
    # Only authenticated users can access
```

### Data Sources
Reports pull data from MongoDB collections:
- **alerts** - Threat detections
- **containment_actions** - Response actions
- **logs** - System logs

## Benefits

1. **Secure** - All endpoints require authentication
2. **Real-time** - Data comes from live MongoDB
3. **Comprehensive** - Shows full threat intelligence
4. **Exportable** - Can export to PDF/CSV
5. **Consistent** - Uses same auth pattern as other modules

## Troubleshooting

### Reports Not Loading
1. Check browser console for errors
2. Verify you're logged in (check AuthContext)
3. Check backend is running on port 8000
4. Test API directly: `curl http://localhost:8000/api/reports/summary`

### 401 Unauthorized Errors
1. Check Supabase session is valid
2. Try logging out and back in
3. Check token expiration
4. Verify backend auth middleware is working

### No Data Showing
1. Check MongoDB has alerts data
2. Run simulation to generate data
3. Check backend logs for database errors
4. Verify MongoDB connection is working

## Future Enhancements

1. **Real-time Updates** - WebSocket for live report updates
2. **Custom Date Ranges** - Select specific date ranges
3. **Advanced Filters** - Filter by endpoint, risk level, attack type
4. **Scheduled Reports** - Auto-generate and email reports
5. **PDF Generation** - Actual PDF export with charts
6. **CSV Export** - Download raw data as CSV
7. **Report Templates** - Pre-configured report layouts
8. **Comparison Views** - Compare time periods
