const BASE_URL = '/api'

async function request(method, path, body = null, params = null) {
  let url = `${BASE_URL}${path}`

  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value)
      }
    })
    const qs = searchParams.toString()
    if (qs) url += `?${qs}`
  }

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  }

  if (body) {
    options.body = JSON.stringify(body)
  }

  try {
    const response = await fetch(url, options)

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      try {
        const errorBody = await response.json()
        errorMessage = errorBody.detail || errorBody.message || errorMessage
      } catch {
        // use default error message
      }
      throw new Error(errorMessage)
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }

    return null
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Cannot connect to server. Please check your connection.')
    }
    throw error
  }
}

const get = (path, params) => request('GET', path, null, params)
const post = (path, body) => request('POST', path, body)
const put = (path, body) => request('PUT', path, body)

export const api = {
  createUser: (data) => post('/users', data),
  getUser: (id) => get(`/users/${id}`),
  updateInterests: (id, interests) => put(`/users/${id}/interests`, { interests }),
  getFeed: (userId) => get(`/feed/${userId}`),
  recordInteraction: (userId, snippetId, action) =>
    post(`/feed/${userId}/interact`, { snippet_id: snippetId, action }),
  getSnippets: (params) => get('/snippets', params),
  getAudioUrl: (snippetId) => `/api/snippets/${snippetId}/audio`,
  getCategories: () => get('/admin/categories'),
  healthCheck: () => get('/health'),
}
