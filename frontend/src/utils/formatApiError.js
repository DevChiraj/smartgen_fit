export function formatApiError(error, fallback = 'Something went wrong. Please try again.') {
  const message = error?.response?.data?.message

  if (!message) return fallback
  if (typeof message === 'string') return message

  if (typeof message === 'object') {
    return Object.entries(message)
      .map(([field, fieldErrors]) => {
        const text = Array.isArray(fieldErrors) ? fieldErrors.join(', ') : fieldErrors
        return `${field}: ${text}`
      })
      .join(' | ')
  }

  return fallback
}
