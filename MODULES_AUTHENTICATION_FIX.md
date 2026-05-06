# Modules Authentication Fix

## Issues Fixed

### 1. Reports Module
**Problem**: Not working due to authentication issues
**Solution**: 
- Added `supabase` import to ReportsModule
- Updated to use direct import instead of `window.supabase`
- Added proper error handling for authentication failures
- Added token validation before making API calls

### 2. Risk Overview Module  
**Problem**: Getting 500 Internal Server Error
**Root Causes**:
1. Backend timezone error: `timezone(timedelta(...))` is invalid syntax
2. Missing authentication headers in frontend requests

**Solutions**:
- **Backend** (`backend/api/routes.py`):
  - Created IST timezone constant: `IST = timezone(timedelta(hours=5, minutes=30))`
  - Replaced all `timezone(timedelta(...))` with `IST`
  - Fixed risk-overview endpoints to use proper timezone

- **Frontend** (`frontend/src/components/RiskOverview.jsx`):
  - Added `supabase` import
  - Added authentication token to all API requests
  - Added proper error handling for 401 and 500 errors
  - Added token validation before making requests

### 3. Settings Module
**Problem**: Using `window.supabase` which might not be defined
**Solution**:
- Added direct `supabase` import
- Replaced `window.supabase?.auth.getSession()` with `supabase.auth.getSession()`

### 4. Network Topology Module
**Problem**: Using `window.supabase` which might not be defined
**Solution**:
- Added direct `supabase` import
- Replaced `window.supabase?.auth.getSession()` with `supabase.auth.getSession()`

### 5. Global Supabase Access
**Enhancement**: Added `window.supabase` for backward compatibility
**File**: `frontend/src/main.jsx`
- Exposed supabase globally: `window.supabase = supabase`
- Ensures any code using `window.supabase` still works

## Files Modified

### Backend
1. `backend/api/routes.py`
   - Added IST timezone constant
   - Fixed timezone usage in risk-overview endpoints

### Frontend
1. `frontend/src/main.jsx`
   - Exposed supabase globally

2. `frontend/src/components/ReportsModule.jsx`
   - Added supabase import
   - Updated authentication handling
   - Added error handling

3. `frontend/src/components/RiskOverview.jsx`
   - Added supabase import
   - Added authentication headers to all requests
   - Enhanced error handling

4. `frontend/src/components/SettingsModule.jsx`
   - Added supabase import
   - Updated authentication handling

5. `frontend/src/components/NetworkTopologyAdvanced.jsx`
   - Added supabase import
   - Updated authentication handling

## Testing

### Test Reports Module
1. Navigate to `/reports`
2. Should see threat intelligence reports
3. Should see charts and incident data
4. Export buttons should work

### Test Risk Overview Module
1. Navigate to `/risk-overview`
2. Should see global risk score
3. Should see endpoint risks table
4. Should see risk trend chart
5. No 500 errors in console

### Test Settings Module
1. Navigate to `/settings`
2. Should load current settings
3. Should be able to change thresholds
4. Should be able to toggle options
5. Save should work

### Test Network Topology
1. Navigate to `/network-topology`
2. Should load network graph
3. Should show nodes and connections
4. No authentication errors

## Common Authentication Pattern

All modules now follow this pattern:

```javascript
import { supabase } from '../lib/supabase'

const fetchData = async () => {
  try {
    // Get authentication token
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token
    
    if (!token) {
      console.error('No authentication token')
      return
    }
    
    const headers = { Authorization: `Bearer ${token}` }
    
    // Make API call with headers
    const response = await apiClient.get('/api/endpoint', { headers })
    
    // Process data
    setData(response.data)
  } catch (error) {
    console.error('Error:', error)
    if (error.response?.status === 401) {
      // Handle authentication error
    }
  }
}
```

## Benefits

1. **Consistent Authentication**: All modules use the same pattern
2. **Better Error Handling**: Specific messages for different error types
3. **Type Safety**: Direct imports instead of global window object
4. **Debugging**: Easier to trace authentication issues
5. **Maintainability**: Single source of truth for supabase client

## Troubleshooting

### Module Shows "Authentication Required"
- Check if user is logged in
- Check browser console for Supabase errors
- Verify Supabase credentials in `.env`

### Module Shows "Server Error"
- Check backend terminal for Python errors
- Verify backend is running on port 8000
- Check MongoDB connection

### Module Shows "Failed to Load Data"
- Check if backend is running
- Verify frontend can reach backend
- Run `test_connection.ps1` to diagnose

## Next Steps

All major modules now have proper authentication and error handling. The system should work smoothly with:
- Real-time settings updates
- Proper authentication across all modules
- Better error messages for debugging
