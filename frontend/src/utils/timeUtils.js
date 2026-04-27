/**
 * Time Utility Functions for ARCS Dashboard
 * Handles UTC to IST conversion and formatting
 */

/**
 * Convert UTC timestamp to IST and format as time only
 * @param {string|Date} value - UTC timestamp
 * @returns {string} Formatted time in IST (e.g., "02:30:45 PM")
 */
export const formatTimeIST = (value) => {
  if (!value) return '--'
  
  try {
    const date = new Date(value)
    
    // Check if valid date
    if (isNaN(date.getTime())) return '--'
    
    // Format in IST timezone
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    })
  } catch (error) {
    console.error('Error formatting time:', error)
    return '--'
  }
}

/**
 * Convert UTC timestamp to IST and format as full date-time
 * @param {string|Date} value - UTC timestamp
 * @returns {string} Formatted date-time in IST (e.g., "26 Apr 2026, 02:30:45 PM")
 */
export const formatDateTimeIST = (value) => {
  if (!value) return '--'
  
  try {
    const date = new Date(value)
    
    // Check if valid date
    if (isNaN(date.getTime())) return '--'
    
    // Format in IST timezone
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    })
  } catch (error) {
    console.error('Error formatting date-time:', error)
    return '--'
  }
}

/**
 * Get relative time (e.g., "5 minutes ago", "2 hours ago")
 * @param {string|Date} value - UTC timestamp
 * @returns {string} Relative time string
 */
export const getRelativeTime = (value) => {
  if (!value) return '--'
  
  try {
    const date = new Date(value)
    const now = new Date()
    
    // Check if valid date
    if (isNaN(date.getTime())) return '--'
    
    const diffMs = now - date
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)
    
    if (diffSec < 60) {
      return 'Just now'
    } else if (diffMin < 60) {
      return `${diffMin} min${diffMin > 1 ? 's' : ''} ago`
    } else if (diffHour < 24) {
      return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`
    } else if (diffDay < 7) {
      return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`
    } else {
      return formatDateTimeIST(value)
    }
  } catch (error) {
    console.error('Error calculating relative time:', error)
    return '--'
  }
}

/**
 * Get current time in IST
 * @returns {string} Current time in IST
 */
export const getCurrentTimeIST = () => {
  return new Date().toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
}

/**
 * Format time for chart labels (short format)
 * @param {string|Date} value - UTC timestamp
 * @returns {string} Short time format (e.g., "14:30")
 */
export const formatChartTime = (value) => {
  if (!value) return '--'
  
  try {
    const date = new Date(value)
    
    // Check if valid date
    if (isNaN(date.getTime())) return '--'
    
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'Asia/Kolkata'
    })
  } catch (error) {
    console.error('Error formatting chart time:', error)
    return '--'
  }
}
