const BASE_URL = 'https://general-service-staging.up.railway.app/api'

const TOKEN_KEY = 'humana-checkin-lite.access-token'
const REFRESH_TOKEN_KEY = 'humana-checkin-lite.refresh-token'
const USER_KEY = 'humana-checkin-lite.api-user'

export interface ApiUser {
  id: string
  name: string
  cpf?: string
  email?: string
  [key: string]: unknown
}

export interface ApiTokens {
  access_token: string
  refresh_token?: string
  token_type: string
}

export interface ApiAddress {
  street?: string
  number?: string
  complement?: string
  neighborhood?: string
  city?: string
  uf?: string
  zip_code?: string
}

export interface ApiInstitution {
  id: string
  name?: string
  display_name?: string
  social_name?: string
  address?: string | ApiAddress
  lat?: number
  long?: number
  latitude?: number
  longitude?: number
}

export interface ApiUserShift {
  id: string
  institution_id?: string
  institution?: ApiInstitution
  user_id?: string | null
  user?: { id?: string; first_name?: string; last_name?: string; name?: string; [key: string]: unknown } | null
  sector?: { id: string; display_name?: string; name?: string }
  date?: string
  planned_start?: string
  planned_end?: string
  start_time?: string
  end_time?: string
  status?: string
  agreed_value?: number
  checkin_time?: string
  checkout_time?: string
  [key: string]: unknown
}

interface FirstLoginCheckResponse {
  has_password: boolean
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredUser(): ApiUser | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as ApiUser
  } catch {
    return null
  }
}

export function clearApiSession(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) ?? {}),
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`${res.status} ${body}`)
  }
  const ct = res.headers.get('content-type') ?? ''
  if (ct.includes('application/json')) return res.json() as Promise<T>
  return res.text() as unknown as T
}

export async function apiLogin(cpf: string, password: string): Promise<{ user: ApiUser }> {
  const tokens = await request<ApiTokens>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ cpf, password, remember_me: true }),
  })
  localStorage.setItem(TOKEN_KEY, tokens.access_token)
  if (tokens.refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
  const user = await request<ApiUser>('/auth/me')
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  return { user }
}

export async function apiRefreshToken(): Promise<boolean> {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
  if (!refresh) return false
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    })
    if (!res.ok) return false
    const tokens = (await res.json()) as ApiTokens
    localStorage.setItem(TOKEN_KEY, tokens.access_token)
    if (tokens.refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
    return true
  } catch {
    return false
  }
}

export async function apiGetInstitutions(): Promise<ApiInstitution[]> {
  const result = await request<ApiInstitution[] | { items?: ApiInstitution[]; data?: ApiInstitution[] }>(
    '/institutions',
  )
  if (Array.isArray(result)) return result
  return result.items ?? result.data ?? []
}

export async function apiGetUserShifts(
  institutionId: string,
  dateYYYYMM: string,
  userId?: string,
): Promise<ApiUserShift[]> {
  const params = new URLSearchParams({ institution_id: institutionId, date: dateYYYYMM })
  if (userId) params.set('user_id', userId)
  const result = await request<unknown>(`/user-shifts?${params}`)
  if (!Array.isArray(result)) return []
  const first = result[0]
  if (first && typeof first === 'object' && 'shifts' in (first as object)) {
    return (result as Array<{ shifts: ApiUserShift[] }>).flatMap((g) => g.shifts)
  }
  return result as ApiUserShift[]
}

export async function apiIsCpfRegistered(cpf: string): Promise<{
  registered: boolean
  active: boolean
  status?: string
  name?: string
  id?: string
}> {
  try {
    const result = await request<{
      user_id?: string
      status?: string
      is_registered?: boolean
      registered?: boolean
      name?: string
      id?: string
    } | null>(`/users/is-registered/${cpf}`)

    if (!result) return { registered: false, active: false }

    if (result.user_id) {
      const name = await apiGetUserName(result.user_id)
      const status = String(result.status ?? '').toUpperCase()
      return { registered: true, active: status === 'ACTIVE', status, id: result.user_id, name }
    }
    const registered = result.is_registered ?? result.registered ?? false
    const status = String(result.status ?? '').toUpperCase()
    return {
      registered: Boolean(registered),
      active: status === 'ACTIVE',
      status,
      name: result.name,
      id: result.id,
    }
  } catch {
    return { registered: false, active: false }
  }
}

export async function apiCheckFirstLogin(cpf: string): Promise<FirstLoginCheckResponse> {
  return request<FirstLoginCheckResponse>('/first-login/check', {
    method: 'POST',
    body: JSON.stringify({ cpf }),
  })
}

export async function apiSendFirstLoginToken(cpf: string): Promise<void> {
  await request<unknown>('/first-login/send-token', {
    method: 'POST',
    body: JSON.stringify({ cpf }),
  })
}

export async function apiResetFirstLoginPassword(token: string, newPassword: string): Promise<void> {
  await request<unknown>('/first-login/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  })
}

export async function apiForgotPassword(cpf: string): Promise<void> {
  await request<unknown>('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ cpf }),
  })
}

export async function apiResetPassword(token: string, newPassword: string): Promise<void> {
  await request<unknown>('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  })
}

async function apiGetUserName(userId: string): Promise<string | undefined> {
  try {
    const user = await request<{ first_name?: string; last_name?: string; name?: string }>(`/users/${userId}`)
    if (user.first_name || user.last_name) {
      return `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim()
    }
    return user.name
  } catch {
    return undefined
  }
}

export interface ApiUserShiftPatch {
  user_id?: string | null
  status?: string
  checkin_time?: string
  checkin_lat?: number
  checkin_long?: number
  checkout_time?: string
  [key: string]: unknown
}

export async function apiUpdateUserShift(shiftId: string, patch: ApiUserShiftPatch): Promise<ApiUserShift> {
  return request<ApiUserShift>(`/user-shifts/${shiftId}`, {
    method: 'PUT',
    body: JSON.stringify(patch),
  })
}

export function mapApiShiftStatus(status: string | undefined): 'available' | 'active' | 'completed' {
  switch ((status ?? '').toUpperCase()) {
    case 'ACTIVE':
    case 'IN_PROGRESS':
    case 'CHECKED_IN':
      return 'active'
    case 'COMPLETED':
    case 'DONE':
    case 'FINISHED':
    case 'CHECKED_OUT':
      return 'completed'
    default:
      return 'available'
  }
}
