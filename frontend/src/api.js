const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Thin fetch wrapper. Throws a readable Error on non-2xx responses so
 * components can show the actual problem instead of a generic failure.
 */
async function request(path, params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, value)
    }
  })

  let response
  try {
    response = await fetch(`${BASE_URL}${path}?${query.toString()}`)
  } catch (err) {
    throw new Error(
      `Could not reach the API at ${BASE_URL}. Is the backend running? (uvicorn main:app --reload)`
    )
  }

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new Error(detail)
  }

  return response.json()
}

export function predict(params) {
  return request('/api/predict', params)
}

export function getUniversities() {
  return request('/api/universities')
}
