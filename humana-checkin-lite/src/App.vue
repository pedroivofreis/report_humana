<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import HospitalHeading from './components/HospitalHeading.vue'
import {
  apiIsCpfRegistered,
  apiGetInstitutions,
  apiGetUserShifts,
  apiCheckin,
  apiCheckout,
  getStoredToken,
  getStoredUser,
  clearApiSession,
  mapApiShiftStatus,
  type ApiUser,
  type ApiInstitution,
} from './api'

type ShiftStatus = 'available' | 'active' | 'completed'
type BottomTabId = 'myShifts' | 'calendar' | 'announcements' | 'finance' | 'account'
type ModalMode = 'start' | 'stop'

interface Doctor {
  id: string
  name: string
  cpf: string
  apiId?: string
}

interface Coords {
  lat: number
  lng: number
}

interface CheckLocation {
  lat: number
  lng: number
  accuracyMeters: number
  distanceToHospitalMeters: number
  within500m: boolean
}

interface CheckLog {
  timestamp: string
  imageDataUrl?: string
  imageCode?: string
  location: CheckLocation
  device: string
  ip: string
}

interface ReviewData {
  text: string
  submittedAt: string
}

interface Shift {
  id: string
  hospitalName: string
  hospitalLogoUrl?: string
  hospitalAddress: string
  hospitalCoords: Coords
  date: string
  startTime: string
  endTime: string
  status: ShiftStatus
  checkIn?: CheckLog
  checkOut?: CheckLog
  review?: ReviewData
}

interface AnnouncementShift {
  id: string
  hospitalName: string
  hospitalLogoUrl?: string
  hospitalAddress: string
  hospitalCoords: Coords
  date: string
  startTime: string
  endTime: string
  specialty: string
}

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

interface SyncQueueItem {
  id: string
  action: 'login' | 'take-announcement' | 'start-shift' | 'stop-shift' | 'submit-review'
  payload: Record<string, string>
  createdAt: string
  status: 'pending' | 'synced'
  syncedAt?: string
}

const SESSION_KEY = 'humana-checkin-lite.session'
const SHIFTS_KEY_PREFIX = 'humana-checkin-lite.shifts.'
const ANNOUNCEMENTS_KEY_PREFIX = 'humana-checkin-lite.announcements.'
const SYNC_QUEUE_KEY = 'humana-checkin-lite.sync-queue'
const ALERTS_KEY_PREFIX = 'humana-checkin-lite.alerts.'
const TODAY_MOCK_SHIFTS_MIN = 3

function formatIsoDate(date: Date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
}

function mockTodayIso(): string {
  return formatIsoDate(new Date())
}

function mockIsoPlusDays(offsetDays: number): string {
  const d = new Date()
  d.setDate(d.getDate() + offsetDays)
  return formatIsoDate(d)
}

const doctors: Doctor[] = [
  { id: 'doc-1', name: 'Dra. Mariana Costa', cpf: '11122233344' },
  { id: 'doc-2', name: 'Dr. Rafael Lima', cpf: '55566677788' },
]

const doctorShiftSeeds: Record<string, Shift[]> = {
  'doc-1': [
    {
      id: 'm-1001',
      hospitalName: 'Hospital Humana Centro',
      hospitalAddress: 'Rua das Flores, 100 - Centro',
      hospitalCoords: { lat: -23.5505, lng: -46.6333 },
      date: mockTodayIso(),
      startTime: '07:00',
      endTime: '13:00',
      status: 'available',
    },
    {
      id: 'm-1002',
      hospitalName: 'Hospital Humana Norte',
      hospitalAddress: 'Av. Norte, 250 - Santana',
      hospitalCoords: { lat: -23.5016, lng: -46.6205 },
      date: mockIsoPlusDays(1),
      startTime: '19:00',
      endTime: '07:00',
      status: 'available',
    },
    {
      id: 'm-1003',
      hospitalName: 'Hospital Humana Sul',
      hospitalAddress: 'Rua Sul, 480 - Vila Mariana',
      hospitalCoords: { lat: -23.5899, lng: -46.6347 },
      date: mockIsoPlusDays(4),
      startTime: '13:00',
      endTime: '19:00',
      status: 'available',
    },
  ],
  'doc-2': [
    {
      id: 'm-2001',
      hospitalName: 'Hospital Humana Oeste',
      hospitalAddress: 'Av. Oeste, 900 - Perdizes',
      hospitalCoords: { lat: -23.5314, lng: -46.6785 },
      date: mockTodayIso(),
      startTime: '07:00',
      endTime: '19:00',
      status: 'available',
    },
    {
      id: 'm-2002',
      hospitalName: 'Hospital Humana Leste',
      hospitalAddress: 'Rua Leste, 1200 - Tatuape',
      hospitalCoords: { lat: -23.5364, lng: -46.5767 },
      date: mockIsoPlusDays(3),
      startTime: '19:00',
      endTime: '07:00',
      status: 'available',
    },
  ],
}

const doctorAnnouncementSeeds: Record<string, AnnouncementShift[]> = {
  'doc-1': [
    {
      id: 'a-3001',
      hospitalName: 'Hospital Humana Butanta',
      hospitalAddress: 'Rua Piraja, 80 - Butanta',
      hospitalCoords: { lat: -23.5717, lng: -46.7083 },
      date: mockTodayIso(),
      startTime: '07:00',
      endTime: '13:00',
      specialty: 'Clinica Medica',
    },
    {
      id: 'a-3002',
      hospitalName: 'Hospital Humana Guarulhos',
      hospitalAddress: 'Av. Monteiro Lobato, 1200 - Centro',
      hospitalCoords: { lat: -23.4611, lng: -46.5331 },
      date: mockIsoPlusDays(3),
      startTime: '19:00',
      endTime: '07:00',
      specialty: 'Urgencia',
    },
    {
      id: 'a-3003',
      hospitalName: 'Hospital Humana Pinheiros',
      hospitalAddress: 'Rua dos Pinheiros, 498 - Pinheiros',
      hospitalCoords: { lat: -23.5632, lng: -46.6881 },
      date: mockIsoPlusDays(1),
      startTime: '13:00',
      endTime: '19:00',
      specialty: 'Clinica Medica',
    },
    {
      id: 'a-3004',
      hospitalName: 'Hospital Humana Mooca',
      hospitalAddress: 'Rua Taquari, 120 - Mooca',
      hospitalCoords: { lat: -23.5497, lng: -46.5934 },
      date: mockIsoPlusDays(5),
      startTime: '07:00',
      endTime: '13:00',
      specialty: 'Pediatria',
    },
    {
      id: 'a-3005',
      hospitalName: 'Hospital Humana Santo Amaro',
      hospitalAddress: 'Av. Santo Amaro, 2468 - Santo Amaro',
      hospitalCoords: { lat: -23.6289, lng: -46.6704 },
      date: mockIsoPlusDays(7),
      startTime: '19:00',
      endTime: '07:00',
      specialty: 'UTI Adulto',
    },
  ],
  'doc-2': [
    {
      id: 'a-4001',
      hospitalName: 'Hospital Humana Osasco',
      hospitalAddress: 'Rua Antonio Agu, 410 - Centro',
      hospitalCoords: { lat: -23.5328, lng: -46.7917 },
      date: mockTodayIso(),
      startTime: '13:00',
      endTime: '19:00',
      specialty: 'Clinica Medica',
    },
    {
      id: 'a-4002',
      hospitalName: 'Hospital Humana Alphaville',
      hospitalAddress: 'Al. Rio Negro, 200 - Alphaville',
      hospitalCoords: { lat: -23.4945, lng: -46.8512 },
      date: mockIsoPlusDays(2),
      startTime: '07:00',
      endTime: '13:00',
      specialty: 'Cardiologia',
    },
    {
      id: 'a-4003',
      hospitalName: 'Hospital Humana Morumbi',
      hospitalAddress: 'Av. Giovanni Gronchi, 4500 - Morumbi',
      hospitalCoords: { lat: -23.6314, lng: -46.7254 },
      date: mockIsoPlusDays(4),
      startTime: '19:00',
      endTime: '07:00',
      specialty: 'Urgencia',
    },
    {
      id: 'a-4004',
      hospitalName: 'Hospital Humana Paulista',
      hospitalAddress: 'Av. Paulista, 2200 - Bela Vista',
      hospitalCoords: { lat: -23.5614, lng: -46.656 },
      date: mockIsoPlusDays(1),
      startTime: '13:00',
      endTime: '19:00',
      specialty: 'Clinica Medica',
    },
    {
      id: 'a-4005',
      hospitalName: 'Hospital Humana Ibirapuera',
      hospitalAddress: 'Av. Ibirapuera, 3200 - Moema',
      hospitalCoords: { lat: -23.6034, lng: -46.6624 },
      date: mockIsoPlusDays(6),
      startTime: '07:00',
      endTime: '19:00',
      specialty: 'Ortopedia',
    },
  ],
}

const activeTab = ref<BottomTabId>('myShifts')
const currentDoctor = ref<Doctor | null>(null)
const shifts = ref<Shift[]>([])
const announcements = ref<AnnouncementShift[]>([])
const loginCpf = ref('')
const loginError = ref('')
const loginLoading = ref(false)
const appFeedback = ref('')
const installFeedback = ref('')
const apiInstitutions = ref<ApiInstitution[]>([])
const nowTick = ref(Date.now())
const installPromptEvent = ref<BeforeInstallPromptEvent | null>(null)
const isStandalone = ref(false)
const isOnline = ref(navigator.onLine)
const syncQueue = ref<SyncQueueItem[]>([])
const alertsEnabled = ref(true)
const shiftListFilter = ref<'all' | 'today' | 'scheduled'>('all')
/** Sub-abas dentro de Meus plantões */
const shiftListSegment = ref<'upcoming' | 'completed'>('upcoming')
const financeHospitalFilter = ref('all')
const financeStatusFilter = ref<'all' | ShiftStatus>('all')

const shiftModal = reactive({
  open: false,
  shiftId: '',
  mode: 'start' as ModalMode,
  step: 'summary' as 'summary' | 'check',
  imageDataUrl: '',
  imageCode: '',
  isPhotoConfirmed: false,
  cameraError: '',
  isStartingCamera: false,
  location: null as CheckLocation | null,
  locationError: '',
  ip: '',
  isCollectingContext: false,
  formError: '',
})

const reviewModal = reactive({
  open: false,
  shiftId: '',
  text: '',
  error: '',
})

const announcementModal = reactive({
  open: false,
  announcementId: '',
})

const alertsModal = reactive({
  open: false,
  firstAccess: false,
})

let clockInterval: number | undefined
const cameraVideoRef = ref<HTMLVideoElement | null>(null)
let cameraStream: MediaStream | null = null

const maskedCpf = computed(() => formatCpf(loginCpf.value))
const activeShift = computed(() => shifts.value.find((shift) => shift.status === 'active') ?? null)
const selectedShift = computed(() => shifts.value.find((shift) => shift.id === shiftModal.shiftId) ?? null)
const selectedReviewShift = computed(() => shifts.value.find((shift) => shift.id === reviewModal.shiftId) ?? null)
const selectedAnnouncement = computed(
  () => announcements.value.find((announcement) => announcement.id === announcementModal.announcementId) ?? null,
)

/** Aba Anúncios: no máximo 5 ofertas em tela. */
const announcementsVisible = computed(() => announcements.value.slice(0, 5))
const canPromptInstall = computed(() => Boolean(installPromptEvent.value))
const showInstallButton = computed(() => !isStandalone.value)
const calendarMonth = ref(startOfMonth(new Date()))
const selectedCalendarDate = ref(formatIsoDate(new Date()))

const shiftsByDate = computed(() => {
  const grouped = new Map<string, Shift[]>()
  for (const shift of shifts.value) {
    if (!grouped.has(shift.date)) grouped.set(shift.date, [])
    grouped.get(shift.date)?.push(shift)
  }
  for (const [, dateShifts] of grouped) {
    dateShifts.sort((a, b) => (a.startTime > b.startTime ? 1 : -1))
  }
  return grouped
})

const calendarMonthLabel = computed(() =>
  calendarMonth.value.toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric',
  }),
)

const calendarDays = computed(() => buildMonthGrid(calendarMonth.value))
const selectedDateShifts = computed(() => shiftsByDate.value.get(selectedCalendarDate.value) ?? [])
const nextScheduledShift = computed(() => {
  if (activeShift.value) return null
  const available = shifts.value
    .filter((shift) => shift.status === 'available')
    .sort((a, b) => getShiftStartTimestamp(a) - getShiftStartTimestamp(b))
  return available[0] ?? null
})

const doctorFirstName = computed(() => {
  const raw = currentDoctor.value?.name ?? ''
  const trimmed = raw.replace(/^(Dr\.|Dra\.)\s+/i, '').trim()
  return trimmed || raw
})

const nextShiftIsToday = computed(
  () => Boolean(nextScheduledShift.value && nextScheduledShift.value.date === mockTodayIso()),
)

const shiftsForList = computed(() => {
  let list = [...shifts.value]

  if (shiftListSegment.value === 'completed') {
    list = list.filter((s) => s.status === 'completed')
    list.sort((a, b) => {
      const endA = a.checkOut?.timestamp ?? `${a.date}T${a.endTime}:00`
      const endB = b.checkOut?.timestamp ?? `${b.date}T${b.endTime}:00`
      return new Date(endB).getTime() - new Date(endA).getTime()
    })
    return list
  }

  list = list.filter((s) => s.status !== 'completed')

  if (shiftListFilter.value === 'today') {
    list = list.filter((s) => s.date === mockTodayIso())
  } else if (shiftListFilter.value === 'scheduled') {
    list = list.filter((s) => s.status === 'available' && s.date !== mockTodayIso())
  }

  list.sort((a, b) => {
    const today = mockTodayIso()
    const at = a.date === today ? 0 : 1
    const bt = b.date === today ? 0 : 1
    if (at !== bt) return at - bt
    return getShiftStartTimestamp(a) - getShiftStartTimestamp(b)
  })
  return list
})

function isShiftOnToday(shift: Shift): boolean {
  return shift.date === mockTodayIso()
}

function shiftUiVariant(shift: Shift): 'today' | 'active' | 'scheduled' | 'done' {
  if (shift.status === 'completed') return 'done'
  if (shift.status === 'active') return 'active'
  if (shift.status === 'available' && isShiftOnToday(shift)) return 'today'
  return 'scheduled'
}

function mockPayAmountBrlNumber(shift: Shift): number {
  let h = 0
  for (let i = 0; i < shift.id.length; i++) h += shift.id.charCodeAt(i)
  return 1200 + (h % 750)
}

function mockPayForShift(shift: Shift): string {
  return mockPayAmountBrlNumber(shift).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatBrl(amount: number): string {
  return amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const financeHospitals = computed(() => {
  const names = Array.from(new Set(shifts.value.map((shift) => shift.hospitalName)))
  names.sort((a, b) => a.localeCompare(b, 'pt-BR'))
  return names
})

const financeShifts = computed(() => {
  let list =
    financeHospitalFilter.value === 'all'
      ? [...shifts.value]
      : shifts.value.filter((shift) => shift.hospitalName === financeHospitalFilter.value)

  if (financeStatusFilter.value !== 'all') {
    list = list.filter((shift) => shift.status === financeStatusFilter.value)
  }

  list.sort((a, b) => getShiftStartTimestamp(b) - getShiftStartTimestamp(a))
  return list
})

const financeSummary = computed(() => {
  let received = 0
  let toReceive = 0
  for (const s of financeShifts.value) {
    const amt = mockPayAmountBrlNumber(s)
    if (s.status === 'completed') received += amt
    else toReceive += amt
  }
  return {
    shiftCount: financeShifts.value.length,
    receivedBrl: received,
    toReceiveBrl: toReceive,
  }
})

function openMapsForShift(shift: Shift) {
  const q = encodeURIComponent(`${shift.hospitalName} ${shift.hospitalAddress}`)
  window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank', 'noopener,noreferrer')
}

function scrollToShiftCard(shiftId: string) {
  shiftListSegment.value = 'upcoming'
  nextTick(() => {
    document.getElementById(`shift-card-${shiftId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

function formatWeekdayDayMonthYear(isoDate: string) {
  const s = new Date(`${isoDate}T12:00:00`).toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
  return s.charAt(0).toUpperCase() + s.slice(1)
}

watch(
  shifts,
  (newShifts) => {
    if (!currentDoctor.value) return
    localStorage.setItem(`${SHIFTS_KEY_PREFIX}${currentDoctor.value.id}`, JSON.stringify(newShifts))
  },
  { deep: true },
)

watch(
  announcements,
  (newAnnouncements) => {
    if (!currentDoctor.value) return
    localStorage.setItem(
      `${ANNOUNCEMENTS_KEY_PREFIX}${currentDoctor.value.id}`,
      JSON.stringify(newAnnouncements),
    )
  },
  { deep: true },
)

watch(
  syncQueue,
  (newQueue) => {
    localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(newQueue))
  },
  { deep: true },
)

watch(currentDoctor, (doctor) => {
  if (!doctor) return
  localStorage.setItem(SESSION_KEY, doctor.id)
})

watch(alertsEnabled, (enabled) => {
  if (!currentDoctor.value) return
  localStorage.setItem(`${ALERTS_KEY_PREFIX}${currentDoctor.value.id}`, enabled ? '1' : '0')
})

onMounted(() => {
  updateStandaloneMode()
  loadSyncQueue()
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener)
  window.addEventListener('appinstalled', handleAppInstalled)
  window.addEventListener('online', handleConnectivityChange)
  window.addEventListener('offline', handleConnectivityChange)
  restoreSession()
  clockInterval = window.setInterval(() => {
    nowTick.value = Date.now()
  }, 1000)
  if (isOnline.value) flushSyncQueue()
})

onBeforeUnmount(() => {
  if (clockInterval) window.clearInterval(clockInterval)
  stopCameraStream()
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener)
  window.removeEventListener('appinstalled', handleAppInstalled)
  window.removeEventListener('online', handleConnectivityChange)
  window.removeEventListener('offline', handleConnectivityChange)
})

async function restoreSession() {
  const apiUser = getStoredUser()
  const token = getStoredToken()

  if (apiUser && token) {
    const doctor = apiUserToDoctor(apiUser)
    currentDoctor.value = doctor
    shifts.value = loadDoctorShifts(doctor.id)
    announcements.value = loadDoctorAnnouncements(doctor.id)
    applySavedAlertsPreference(doctor.id)
    fetchApiShifts(doctor).catch(() => {})
    return
  }

  const doctorId = localStorage.getItem(SESSION_KEY)
  if (!doctorId) return
  const doctor = doctors.find((item) => item.id === doctorId)
  if (!doctor) return
  currentDoctor.value = doctor
  shifts.value = loadDoctorShifts(doctor.id)
  announcements.value = loadDoctorAnnouncements(doctor.id)
  applySavedAlertsPreference(doctor.id)
}

function apiUserToDoctor(user: ApiUser): Doctor {
  return {
    id: user.id,
    name: String(user.name ?? ''),
    cpf: String(user.cpf ?? ''),
    apiId: user.id,
  }
}

async function fetchApiShifts(_doctor?: Doctor) {
  const userId = currentDoctor.value?.apiId
  try {
    let institutions = apiInstitutions.value
    if (institutions.length === 0) {
      institutions = await apiGetInstitutions()
      apiInstitutions.value = institutions
    }
    if (institutions.length === 0) return

    const today = new Date()
    const months = [
      `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`,
    ]
    if (today.getMonth() < 11) {
      const next = new Date(today.getFullYear(), today.getMonth() + 1, 1)
      months.push(`${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, '0')}`)
    }

    const allShifts: Shift[] = []
    for (const inst of institutions) {
      for (const month of months) {
        const apiShifts = await apiGetUserShifts(inst.id, month, userId)
        for (const s of apiShifts) {
          allShifts.push(apiShiftToShift(s, inst))
        }
      }
    }

    if (allShifts.length > 0) {
      shifts.value = mergeApiShiftsWithLocal(allShifts, shifts.value)
    }
  } catch (err) {
    console.warn('[API] shifts fetch failed, keeping local data:', err)
  }
}

function formatApiAddress(address: import('./api').ApiAddress | string | undefined): string {
  if (!address) return ''
  if (typeof address === 'string') return address
  const parts = [
    address.street && address.number ? `${address.street}, ${address.number}` : address.street,
    address.neighborhood,
    address.city && address.uf ? `${address.city} - ${address.uf}` : address.city,
  ].filter(Boolean)
  return parts.join(' - ')
}

function apiShiftToShift(s: import('./api').ApiUserShift, fallbackInstitution?: ApiInstitution): Shift {
  const institution = s.institution ?? fallbackInstitution
  const lat = institution?.lat ?? institution?.latitude ?? -23.5505
  const lng = institution?.long ?? institution?.longitude ?? -46.6333

  const startTime = s.planned_start
    ? s.planned_start.slice(11, 16)
    : (s.start_time ?? '00:00').slice(0, 5)
  const endTime = s.planned_end
    ? s.planned_end.slice(11, 16)
    : (s.end_time ?? '00:00').slice(0, 5)

  const instName = institution?.display_name ?? institution?.name ?? 'Hospital'

  return {
    id: s.id,
    hospitalName: instName,
    hospitalAddress: formatApiAddress(institution?.address),
    hospitalCoords: { lat, lng },
    date: s.date ?? formatIsoDate(new Date()),
    startTime,
    endTime,
    status: mapApiShiftStatus(s.status),
  }
}

function mergeApiShiftsWithLocal(apiShifts: Shift[], localShifts: Shift[]): Shift[] {
  const byId = new Map<string, Shift>()
  for (const s of apiShifts) byId.set(s.id, s)
  for (const s of localShifts) {
    const existing = byId.get(s.id)
    if (existing) {
      byId.set(s.id, { ...existing, status: s.status, checkIn: s.checkIn, checkOut: s.checkOut, review: s.review })
    } else if (s.id.startsWith('mock-') || s.id.startsWith('m-') || s.id.startsWith('a-')) {
      byId.set(s.id, s)
    }
  }
  return Array.from(byId.values())
}

function loadDoctorShifts(doctorId: string) {
  const ensureTodayMockPool = (items: Shift[]) => {
    const today = mockTodayIso()
    const availableToday = items.filter((shift) => shift.date === today && shift.status === 'available')
    if (availableToday.length >= TODAY_MOCK_SHIFTS_MIN) return items

    const seedPool = doctorShiftSeeds[doctorId] ?? []
    if (seedPool.length === 0) return items

    const defaultSlots = [
      { startTime: '07:00', endTime: '13:00' },
      { startTime: '13:00', endTime: '19:00' },
      { startTime: '19:00', endTime: '07:00' },
      { startTime: '08:00', endTime: '14:00' },
      { startTime: '14:00', endTime: '20:00' },
    ]

    const nextItems = [...items]
    const existingIds = new Set(nextItems.map((shift) => shift.id))
    let missing = TODAY_MOCK_SHIFTS_MIN - availableToday.length
    let cursor = 0

    while (missing > 0 && cursor < 12) {
      const seed = structuredClone(seedPool[cursor % seedPool.length])
      const slot = defaultSlots[cursor % defaultSlots.length]
      seed.id = `mock-${doctorId}-${today}-${cursor + 1}`
      seed.date = today
      seed.startTime = slot.startTime
      seed.endTime = slot.endTime
      seed.status = 'available'
      delete seed.checkIn
      delete seed.checkOut
      delete seed.review
      if (!existingIds.has(seed.id)) {
        nextItems.unshift(seed)
        existingIds.add(seed.id)
        missing -= 1
      }
      cursor += 1
    }

    return nextItems
  }

  const saved = localStorage.getItem(`${SHIFTS_KEY_PREFIX}${doctorId}`)
  if (!saved) return ensureTodayMockPool(structuredClone(doctorShiftSeeds[doctorId] ?? []))
  try {
    return ensureTodayMockPool(JSON.parse(saved) as Shift[])
  } catch {
    return ensureTodayMockPool(structuredClone(doctorShiftSeeds[doctorId] ?? []))
  }
}

function padAnnouncementsFromSeeds(doctorId: string, items: AnnouncementShift[]): AnnouncementShift[] {
  const seeds = doctorAnnouncementSeeds[doctorId] ?? []
  const ids = new Set(items.map((x) => x.id))
  const out = [...items]
  for (const seed of seeds) {
    if (out.length >= 5) break
    if (!ids.has(seed.id)) {
      const clone = structuredClone(seed)
      out.push(clone)
      ids.add(seed.id)
    }
  }
  return out
}

function loadDoctorAnnouncements(doctorId: string) {
  const addTodayMockIfMissing = (items: AnnouncementShift[]) => {
    const today = mockTodayIso()
    if (items.some((shift) => shift.date === today)) return items
    const seed = structuredClone((doctorAnnouncementSeeds[doctorId] ?? [])[0])
    if (!seed) return items
    seed.id = `${seed.id}-today`
    seed.date = today
    return [seed, ...items]
  }

  const saved = localStorage.getItem(`${ANNOUNCEMENTS_KEY_PREFIX}${doctorId}`)
  const base = !saved
    ? structuredClone(doctorAnnouncementSeeds[doctorId] ?? [])
    : (() => {
        try {
          return JSON.parse(saved) as AnnouncementShift[]
        } catch {
          return structuredClone(doctorAnnouncementSeeds[doctorId] ?? [])
        }
      })()

  return addTodayMockIfMissing(padAnnouncementsFromSeeds(doctorId, base))
}

function loadSyncQueue() {
  const saved = localStorage.getItem(SYNC_QUEUE_KEY)
  if (!saved) {
    syncQueue.value = []
    return
  }
  try {
    syncQueue.value = JSON.parse(saved) as SyncQueueItem[]
  } catch {
    syncQueue.value = []
  }
}

function getDoctorAlertsPref(doctorId: string): boolean | null {
  const saved = localStorage.getItem(`${ALERTS_KEY_PREFIX}${doctorId}`)
  if (saved === null) return null
  if (saved === '0') return false
  return true
}

function applySavedAlertsPreference(doctorId: string) {
  const saved = getDoctorAlertsPref(doctorId)
  if (saved === null) {
    alertsEnabled.value = false
    openAlertsModal(true)
    return
  }
  alertsEnabled.value = saved
}

async function handleLogin() {
  loginError.value = ''
  appFeedback.value = ''
  const cpf = loginCpf.value.replace(/\D/g, '')
  if (cpf.length !== 11) {
    loginError.value = 'Digite um CPF válido com 11 dígitos.'
    return
  }

  // 1) Tenta CPF mock primeiro (offline/dev)
  const mockDoctor = doctors.find((item) => item.cpf === cpf)
  if (mockDoctor) {
    loginWith(mockDoctor)
    return
  }

  // 2) Verifica na API real
  loginLoading.value = true
  try {
    const { registered, name, id } = await apiIsCpfRegistered(cpf)
    if (!registered) {
      loginError.value = 'Não encontramos médico com este CPF.'
      return
    }
    const doctor: Doctor = {
      id: id ?? cpf,
      name: name ?? 'Médico',
      cpf,
      apiId: id,
    }
    loginWith(doctor)
  } catch {
    loginError.value = 'Erro ao verificar CPF. Verifique sua conexão.'
  } finally {
    loginLoading.value = false
  }
}

function loginWith(doctor: Doctor) {
  currentDoctor.value = doctor
  shifts.value = loadDoctorShifts(doctor.id)
  announcements.value = loadDoctorAnnouncements(doctor.id)
  financeHospitalFilter.value = 'all'
  financeStatusFilter.value = 'all'
  applySavedAlertsPreference(doctor.id)
  activeTab.value = 'myShifts'
  loginCpf.value = ''
  enqueueSyncAction('login', { doctorId: doctor.id, cpf: doctor.cpf })
  fetchApiShifts().catch(() => {})
}

function handleLogout() {
  currentDoctor.value = null
  shifts.value = []
  announcements.value = []
  apiInstitutions.value = []
  financeHospitalFilter.value = 'all'
  financeStatusFilter.value = 'all'
  alertsEnabled.value = true
  localStorage.removeItem(SESSION_KEY)
  clearApiSession()
  closeShiftModal()
  closeReviewModal()
  closeAnnouncementModal()
  closeAlertsModal()
}

function openAlertsModal(firstAccess = false) {
  alertsModal.open = true
  alertsModal.firstAccess = firstAccess
}

function closeAlertsModal() {
  alertsModal.open = false
  alertsModal.firstAccess = false
}

function setAlertsPreference(enabled: boolean) {
  alertsEnabled.value = enabled
  if (currentDoctor.value) {
    localStorage.setItem(`${ALERTS_KEY_PREFIX}${currentDoctor.value.id}`, enabled ? '1' : '0')
  }
  appFeedback.value = enabled ? 'Alertas ativados.' : 'Alertas desativados.'
  closeAlertsModal()
}

function handleBeforeInstallPrompt(event: BeforeInstallPromptEvent) {
  event.preventDefault()
  installPromptEvent.value = event
}

function handleConnectivityChange() {
  isOnline.value = navigator.onLine
  if (isOnline.value) {
    flushSyncQueue()
    appFeedback.value = 'Conexao restaurada. Sincronizando dados salvos offline.'
  } else {
    appFeedback.value = 'Sem internet. Suas acoes serao salvas offline.'
  }
}

function enqueueSyncAction(action: SyncQueueItem['action'], payload: Record<string, string>) {
  syncQueue.value = [
    {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      action,
      payload,
      createdAt: new Date().toISOString(),
      status: 'pending',
    },
    ...syncQueue.value,
  ]
  if (isOnline.value) flushSyncQueue()
}

function flushSyncQueue() {
  syncQueue.value = syncQueue.value.map((item) =>
    item.status === 'pending'
      ? {
          ...item,
          status: 'synced',
          syncedAt: new Date().toISOString(),
        }
      : item,
  )
}

function handleAppInstalled() {
  installPromptEvent.value = null
  updateStandaloneMode()
  installFeedback.value = 'App instalado com sucesso.'
}

function updateStandaloneMode() {
  const navigatorWithStandalone = navigator as Navigator & { standalone?: boolean }
  isStandalone.value =
    window.matchMedia('(display-mode: standalone)').matches || Boolean(navigatorWithStandalone.standalone)
}

async function triggerInstall() {
  if (!installPromptEvent.value) {
    installFeedback.value = 'Use o menu do navegador e selecione "Instalar" ou "Adicionar a tela inicial".'
    return
  }
  installFeedback.value = ''
  await installPromptEvent.value.prompt()
  const choice = await installPromptEvent.value.userChoice
  if (choice.outcome === 'accepted') {
    installFeedback.value = 'Instalacao iniciada.'
  }
  installPromptEvent.value = null
}

function setCalendarMonth(offset: number) {
  const month = new Date(calendarMonth.value)
  month.setMonth(month.getMonth() + offset)
  calendarMonth.value = startOfMonth(month)
}

function selectCalendarDate(isoDate: string) {
  selectedCalendarDate.value = isoDate
}

function hasShiftsInDate(isoDate: string) {
  return (shiftsByDate.value.get(isoDate)?.length ?? 0) > 0
}

function getStatusLabel(status: ShiftStatus) {
  if (status === 'active') return 'Em andamento'
  if (status === 'completed') return 'Realizado'
  return 'Pendente'
}

function canShowPrimaryShiftAction(shift: Shift) {
  if (shift.status === 'active') return true
  if (shift.status !== 'available') return false
  return shift.date === formatIsoDate(new Date())
}

function openShiftModal(shift: Shift) {
  shiftModal.open = true
  shiftModal.shiftId = shift.id
  shiftModal.mode = shift.status === 'active' ? 'stop' : 'start'
  shiftModal.step = 'summary'
  shiftModal.imageDataUrl = ''
  shiftModal.imageCode = ''
  shiftModal.isPhotoConfirmed = false
  shiftModal.cameraError = ''
  shiftModal.location = null
  shiftModal.locationError = ''
  shiftModal.formError = ''
  shiftModal.ip = ''
}

async function proceedToCheckModal() {
  shiftModal.step = 'check'
  if (shiftModal.mode === 'start') await startCameraStream()
  await collectRuntimeContext()
}

function closeShiftModal() {
  stopCameraStream()
  shiftModal.open = false
  shiftModal.shiftId = ''
  shiftModal.step = 'summary'
  shiftModal.formError = ''
}

function openReviewModal(shift: Shift) {
  reviewModal.open = true
  reviewModal.shiftId = shift.id
  reviewModal.text = shift.review?.text ?? ''
  reviewModal.error = ''
}

function closeReviewModal() {
  reviewModal.open = false
  reviewModal.shiftId = ''
  reviewModal.text = ''
  reviewModal.error = ''
}

function openAnnouncementModal(announcement: AnnouncementShift) {
  announcementModal.open = true
  announcementModal.announcementId = announcement.id
}

function closeAnnouncementModal() {
  announcementModal.open = false
  announcementModal.announcementId = ''
}

function takeAnnouncementShift() {
  if (!selectedAnnouncement.value) return
  const announcement = selectedAnnouncement.value
  const newShift: Shift = {
    id: announcement.id,
    hospitalName: announcement.hospitalName,
    hospitalLogoUrl: announcement.hospitalLogoUrl,
    hospitalAddress: announcement.hospitalAddress,
    hospitalCoords: announcement.hospitalCoords,
    date: announcement.date,
    startTime: announcement.startTime,
    endTime: announcement.endTime,
    status: 'available',
  }

  shifts.value = [newShift, ...shifts.value]
  announcements.value = announcements.value.filter((item) => item.id !== announcement.id)
  enqueueSyncAction('take-announcement', { announcementId: announcement.id, shiftId: newShift.id })
  appFeedback.value = 'Plantao pego com sucesso. Ele ja aparece em Meus plantoes e Calendario.'
  activeTab.value = 'calendar'
  closeAnnouncementModal()
}

async function collectRuntimeContext() {
  if (!selectedShift.value) return
  shiftModal.isCollectingContext = true
  shiftModal.locationError = ''
  try {
    const [location, ip] = await Promise.all([resolveCurrentLocation(selectedShift.value.hospitalCoords), resolveIp()])
    shiftModal.location = location
    shiftModal.ip = ip
  } catch (error) {
    shiftModal.location = null
    shiftModal.locationError =
      error instanceof Error ? error.message : 'Nao foi possivel coletar localizacao neste dispositivo.'
    shiftModal.ip = await resolveIp()
  } finally {
    shiftModal.isCollectingContext = false
  }
}

async function startCameraStream() {
  shiftModal.cameraError = ''
  shiftModal.isStartingCamera = true
  try {
    stopCameraStream()
    await nextTick()
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user' },
      audio: false,
    })
    cameraStream = stream
    if (!cameraVideoRef.value) throw new Error('Componente de camera indisponivel.')
    cameraVideoRef.value.srcObject = stream
    await cameraVideoRef.value.play()
  } catch (error) {
    shiftModal.cameraError =
      error instanceof Error ? error.message : 'Nao foi possivel abrir a camera neste dispositivo.'
  } finally {
    shiftModal.isStartingCamera = false
  }
}

function stopCameraStream() {
  if (!cameraStream) return
  for (const track of cameraStream.getTracks()) track.stop()
  cameraStream = null
}

async function capturePhotoFromCamera() {
  if (!cameraVideoRef.value) {
    shiftModal.cameraError = 'Camera indisponivel.'
    return
  }
  const video = cameraVideoRef.value
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    shiftModal.cameraError = 'Aguardando camera inicializar. Tente novamente em 1 segundo.'
    return
  }
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const context = canvas.getContext('2d')
  if (!context) {
    shiftModal.cameraError = 'Falha ao capturar imagem da camera.'
    return
  }
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  shiftModal.imageDataUrl = canvas.toDataURL('image/jpeg', 0.92)
  shiftModal.imageCode = await generateImageCodeFromDataUrl(shiftModal.imageDataUrl)
  shiftModal.isPhotoConfirmed = true
  stopCameraStream()
}

async function retakePhoto() {
  shiftModal.isPhotoConfirmed = false
  shiftModal.imageDataUrl = ''
  shiftModal.imageCode = ''
  await startCameraStream()
}

async function confirmShiftAction() {
  shiftModal.formError = ''
  if (!selectedShift.value) return

  // TODO: reativar quando geofence estiver pronto
  // if (!shiftModal.location) {
  //   shiftModal.formError = 'Precisamos da localizacao para registrar o check-in.'
  //   return
  // }
  // if (!shiftModal.location.within500m) {
  //   shiftModal.formError = 'Você precisa estar a menos de 500m do hospital para fazer check-in.'
  //   return
  // }

  if (shiftModal.mode === 'start' && !shiftModal.imageDataUrl) {
    shiftModal.formError = 'Para iniciar, tire uma foto pela camera.'
    return
  }

  const payload: CheckLog = {
    timestamp: new Date().toISOString(),
    imageDataUrl: shiftModal.imageDataUrl || undefined,
    imageCode: shiftModal.imageCode || undefined,
    location: shiftModal.location ?? { lat: 0, lng: 0, accuracyMeters: 0, distanceToHospitalMeters: 0, within500m: false },
    device: getDeviceDescription(),
    ip: shiftModal.ip || 'nao-detectado',
  }

  if (shiftModal.mode === 'start') {
    updateShift(selectedShift.value.id, {
      status: 'active',
      checkIn: payload,
      checkOut: undefined,
      review: undefined,
    })
    appFeedback.value = 'Plantao iniciado com sucesso.'
    enqueueSyncAction('start-shift', { shiftId: selectedShift.value.id, timestamp: payload.timestamp })
    if (isOnline.value && currentDoctor.value?.apiId && shiftModal.location) {
      apiCheckin(currentDoctor.value.apiId, shiftModal.location.lat, shiftModal.location.lng).catch((err) => {
        console.warn('[API] checkin failed:', err)
      })
    }
  } else {
    updateShift(selectedShift.value.id, {
      status: 'completed',
      checkOut: payload,
    })
    activeTab.value = 'myShifts'
    shiftListSegment.value = 'completed'
    appFeedback.value = 'Plantao encerrado e movido para realizados.'
    enqueueSyncAction('stop-shift', { shiftId: selectedShift.value.id, timestamp: payload.timestamp })
    if (isOnline.value && currentDoctor.value?.apiId) {
      apiCheckout(currentDoctor.value.apiId).catch((err) => {
        console.warn('[API] checkout failed:', err)
      })
    }
  }

  closeShiftModal()
}

function submitReview() {
  reviewModal.error = ''
  if (!selectedReviewShift.value) return
  const trimmed = reviewModal.text.trim()
  if (!trimmed) {
    reviewModal.error = 'Digite um texto para enviar a revisao.'
    return
  }

  updateShift(selectedReviewShift.value.id, {
    review: {
      text: trimmed,
      submittedAt: new Date().toISOString(),
    },
  })

  appFeedback.value = 'Revisao enviada com sucesso (mock).'
  enqueueSyncAction('submit-review', { shiftId: selectedReviewShift.value.id })
  closeReviewModal()
}

function updateShift(shiftId: string, patch: Partial<Shift>) {
  shifts.value = shifts.value.map((shift) => {
    if (shift.id !== shiftId) return shift
    return { ...shift, ...patch }
  })
}

function formatCpf(value: string) {
  const digits = value.replace(/\D/g, '').slice(0, 11)
  return digits
    .replace(/^(\d{3})(\d)/, '$1.$2')
    .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1-$2')
}

function formatDate(isoDate: string) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('pt-BR', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function formatDayMonth(isoDate: string) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function formatDateTime(isoDateTime?: string) {
  if (!isoDateTime) return '-'
  return new Date(isoDateTime).toLocaleString('pt-BR')
}

function getShiftStartTimestamp(shift: Shift) {
  return new Date(`${shift.date}T${shift.startTime}:00`).getTime()
}

function formatTimeUntilShift(shift: Shift) {
  const diffMs = getShiftStartTimestamp(shift) - nowTick.value
  if (diffMs <= 0) return `Disponível às ${shift.startTime}`
  const totalSeconds = Math.floor(diffMs / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  if (hours > 0) return `Em ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
  return `Em ${pad(minutes)}:${pad(seconds)}`
}

function formatDistance(distance?: number) {
  if (distance === undefined) return '-'
  return `${Math.round(distance)} m`
}

function formattedElapsed(shift: Shift) {
  if (!shift.checkIn?.timestamp) return '--:--:--'
  const start = new Date(shift.checkIn.timestamp).getTime()
  const end = shift.checkOut?.timestamp ? new Date(shift.checkOut.timestamp).getTime() : nowTick.value
  const diff = Math.max(0, end - start)
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  const s = Math.floor((diff % 60000) / 1000)
  return `${pad(h)}:${pad(m)}:${pad(s)}`
}

function pad(value: number) {
  return value.toString().padStart(2, '0')
}

function getDeviceDescription() {
  const userAgent = navigator.userAgent || 'desconhecido'
  const platform = (navigator as Navigator & { userAgentData?: { platform?: string } }).userAgentData?.platform
  const fallbackPlatform = navigator.platform || 'desconhecido'
  return `${platform ?? fallbackPlatform} | ${userAgent}`
}

async function generateImageCodeFromDataUrl(dataUrl: string) {
  const encoder = new TextEncoder()
  const buffer = encoder.encode(dataUrl)
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map((byte) => byte.toString(16).padStart(2, '0')).join('')
  return hashHex.slice(0, 20)
}

async function resolveCurrentLocation(hospitalCoords: Coords): Promise<CheckLocation> {
  const position = await new Promise<GeolocationPosition>((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocalizacao nao suportada neste dispositivo.'))
      return
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    })
  })

  const distance = calculateDistanceMeters(
    position.coords.latitude,
    position.coords.longitude,
    hospitalCoords.lat,
    hospitalCoords.lng,
  )

  return {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    accuracyMeters: position.coords.accuracy,
    distanceToHospitalMeters: distance,
    within500m: distance <= 500,
  }
}

async function resolveIp() {
  try {
    const response = await fetch('https://api.ipify.org?format=json')
    if (!response.ok) return 'nao-detectado'
    const body = (await response.json()) as { ip?: string }
    return body.ip ?? 'nao-detectado'
  } catch {
    return 'nao-detectado'
  }
}

function calculateDistanceMeters(lat1: number, lon1: number, lat2: number, lon2: number) {
  const earthRadius = 6371000
  const toRad = (value: number) => (value * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return 2 * earthRadius * Math.asin(Math.sqrt(a))
}

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function buildMonthGrid(referenceMonth: Date) {
  const year = referenceMonth.getFullYear()
  const month = referenceMonth.getMonth()
  const firstOfMonth = new Date(year, month, 1)
  const lastOfMonth = new Date(year, month + 1, 0)
  const firstWeekday = firstOfMonth.getDay()
  const daysInMonth = lastOfMonth.getDate()
  const leadingDays = (firstWeekday + 6) % 7
  const totalCells = Math.ceil((leadingDays + daysInMonth) / 7) * 7
  const cells: { isoDate: string; day: number; isCurrentMonth: boolean }[] = []

  for (let index = 0; index < totalCells; index += 1) {
    const dayOffset = index - leadingDays + 1
    const cellDate = new Date(year, month, dayOffset)
    cells.push({
      isoDate: formatIsoDate(cellDate),
      day: cellDate.getDate(),
      isCurrentMonth: cellDate.getMonth() === month,
    })
  }
  return cells
}

</script>

<template>
  <main class="screen">
    <section v-if="!currentDoctor" class="card login-card">
      <div class="login-top-row">
        <div class="brand-lockup">
          <img src="/logo.png" alt="Humana" class="brand-logo" />
        </div>
        <button
          v-if="showInstallButton"
          type="button"
          class="btn-install-pwa"
          :data-ready="canPromptInstall ? 'true' : 'false'"
          @click="triggerInstall"
        >
          <span class="btn-install-pwa__glyph" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M12 3v10" />
              <path d="m8.5 9.5 3.5 3.5 3.5-3.5" />
              <path d="M5 17h14v3a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z" />
            </svg>
          </span>
          <span class="btn-install-pwa__copy">
            <span class="btn-install-pwa__title">Instalar</span>
          </span>
        </button>
      </div>
      <h1>Check-in Lite</h1>
      <p class="description">Entre com seu CPF para acessar seus plantões.</p>
      <p v-if="installFeedback" class="helper">{{ installFeedback }}</p>

      <label for="cpf-input" class="label">CPF do médico</label>
      <input
        id="cpf-input"
        :value="maskedCpf"
        class="input"
        inputmode="numeric"
        maxlength="14"
        placeholder="000.000.000-00"
        autocomplete="username"
        @input="loginCpf = ($event.target as HTMLInputElement).value"
        @keyup.enter="handleLogin"
      />

      <button type="button" class="btn primary big" :disabled="loginLoading" @click="handleLogin">
        {{ loginLoading ? 'Entrando...' : 'Entrar' }}
      </button>

      <p v-if="loginError" class="helper error">{{ loginError }}</p>
    </section>

    <section v-else class="app-shell">
      <section v-if="activeShift" class="active-shift-bar">
        <div>
          <p class="active-label">Plantao em andamento</p>
          <div class="active-meta">
            <HospitalHeading
              :name="activeShift.hospitalName"
              :logo-url="activeShift.hospitalLogoUrl"
              compact
              as="span"
              title-class="active-meta__hospital"
            />
            <span class="active-meta__sep" aria-hidden="true">|</span>
            <span class="active-meta__time">{{ activeShift.startTime }} - {{ activeShift.endTime }}</span>
          </div>
        </div>
        <div class="active-actions">
          <span class="active-timer">{{ formattedElapsed(activeShift) }}</span>
          <button type="button" class="btn danger" @click="openShiftModal(activeShift)">Encerrar plantao</button>
        </div>
      </section>

      <header class="shell-header">
        <div class="shell-header__brand">
          <img src="/logo.png" alt="Humana" class="shell-header__logo" />
          <div class="shell-header__titles">
            <h1 class="shell-header__line">
              <span class="shell-header__hello">Olá, {{ doctorFirstName }}</span>
            </h1>
            <p class="shell-header__sub">Pronto para mais um plantão?</p>
          </div>
        </div>
        <div class="shell-header__actions">
          <button
            type="button"
            class="shell-header__bell"
            :aria-label="alertsEnabled ? 'Alertas ativos' : 'Alertas inativos'"
            @click="openAlertsModal(false)"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
              <path
                d="M14 21a2 2 0 0 1-4 0M18 16H6l1.5-2V10a6 6 0 1 1 12 0v4L18 16z"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linejoin="round"
              />
            </svg>
            <span v-if="!alertsEnabled" class="shell-header__bell-dot" aria-hidden="true"></span>
          </button>
          <button
            v-if="showInstallButton"
            type="button"
            class="btn-install-pwa btn-install-pwa--tiny"
            :data-ready="canPromptInstall ? 'true' : 'false'"
            @click="triggerInstall"
          >
            <span class="btn-install-pwa__glyph" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M12 3v10" />
                <path d="m8.5 9.5 3.5 3.5 3.5-3.5" />
                <path d="M5 17h14v3a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z" />
              </svg>
            </span>
            <span class="btn-install-pwa__copy">
              <span class="btn-install-pwa__title">Instalar</span>
            </span>
          </button>
          <button type="button" class="shell-header__logout" aria-label="Sair" @click="handleLogout">
            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
              <path
                d="M10 17H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h5M14 15l4-3-4-3M18 12H9"
                stroke="currentColor"
                stroke-width="1.85"
                stroke-linecap="round"
                stroke-linejoin="round"
                fill="none"
              />
            </svg>
            <span>Sair</span>
          </button>
        </div>
      </header>

      <p v-if="installFeedback" class="helper shell-install-hint">{{ installFeedback }}</p>

      <button
        v-if="!activeShift && nextScheduledShift"
        type="button"
        class="next-shift-banner"
        @click="scrollToShiftCard(nextScheduledShift.id)"
      >
        <div class="next-shift-banner__clock" aria-hidden="true">
          <svg viewBox="0 0 24 24" class="next-shift-banner__clock-svg">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v6l4 2" />
          </svg>
        </div>
        <div class="next-shift-banner__body">
          <p class="next-shift-banner__eyebrow">{{ nextShiftIsToday ? 'Próximo plantão hoje' : 'Próximo plantão' }}</p>
          <p class="next-shift-banner__countdown">{{ formatTimeUntilShift(nextScheduledShift) }}</p>
          <div class="next-shift-banner__hospital">
            <HospitalHeading
              :name="nextScheduledShift.hospitalName"
              :logo-url="nextScheduledShift.hospitalLogoUrl"
              compact
              as="span"
              title-class="next-shift-banner__hospital-name"
            />
          </div>
        </div>
        <svg class="next-shift-banner__chev" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" />
        </svg>
      </button>

      <p v-if="appFeedback" class="feedback">{{ appFeedback }}</p>

      <section v-if="activeTab === 'myShifts'" class="list list--shifts">
        <div class="my-shifts-head">
          <h3 class="section-heading__title my-shifts-head__title">Meus plantões</h3>

          <div class="segment-tabs" role="tablist" aria-label="Tipo de plantões">
            <button
              type="button"
              class="segment-tabs__btn"
              role="tab"
              :aria-selected="shiftListSegment === 'upcoming'"
              @click="shiftListSegment = 'upcoming'"
            >
              Próximos plantões
            </button>
            <button
              type="button"
              class="segment-tabs__btn"
              role="tab"
              :aria-selected="shiftListSegment === 'completed'"
              @click="shiftListSegment = 'completed'"
            >
              Plantões realizados
            </button>
          </div>

          <div v-if="shiftListSegment === 'upcoming'" class="my-shifts-toolbar">
            <label class="filter-select-wrap">
              <span class="visually-hidden">Filtrar próximos plantões</span>
              <select v-model="shiftListFilter" class="filter-select">
                <option value="all">Todos</option>
                <option value="today">Hoje</option>
                <option value="scheduled">Agendados</option>
              </select>
            </label>
          </div>
        </div>

        <article
          v-for="shift in shiftsForList"
          :id="`shift-card-${shift.id}`"
          :key="shift.id"
          class="shift-ui card"
          :class="{
            'shift-ui--featured': shiftUiVariant(shift) === 'today' || shiftUiVariant(shift) === 'active',
            'shift-ui--scheduled': shiftUiVariant(shift) === 'scheduled',
            'shift-ui--done': shiftUiVariant(shift) === 'done',
          }"
        >
          <template v-if="shiftUiVariant(shift) === 'scheduled'">
            <button type="button" class="shift-ui__row-btn" @click="openMapsForShift(shift)">
              <div class="shift-ui__head shift-ui__head--between">
                <div class="shift-ui__title-wrap">
                  <HospitalHeading
                    :name="shift.hospitalName"
                    :logo-url="shift.hospitalLogoUrl"
                    title-class="shift-ui__title"
                  />
                </div>
                <span class="shift-ui__pill shift-ui__pill--muted">Agendado</span>
              </div>
              <p class="shift-ui__addr">
                <svg class="shift-ui__ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-4.35 7-11a7 7 0 1 0-14 0c0 6.65 7 11 7 11z" fill="none" stroke="currentColor" stroke-width="1.75" /><circle cx="12" cy="10" r="2.25" fill="none" stroke="currentColor" stroke-width="1.75" /></svg>
                {{ shift.hospitalAddress }}
              </p>
              <div class="shift-ui__divider" />
              <div class="shift-ui__meta-row">
                <span class="shift-ui__meta">
                  <svg class="shift-ui__ico-sm" viewBox="0 0 24 24"><rect x="3.5" y="5.5" width="17" height="15" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3.5 9.5h17M8 3.5v4M16 3.5v4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
                  {{ formatWeekdayDayMonthYear(shift.date) }}
                </span>
                <span class="shift-ui__meta shift-ui__meta--with-sep">
                  <svg class="shift-ui__ico-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v6l4 2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                  {{ shift.startTime }} - {{ shift.endTime }}
                </span>
              </div>
              <span class="shift-ui__chev-row" aria-hidden="true">
                <svg class="shift-ui__chev" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none"/></svg>
              </span>
            </button>
            <p v-if="!canShowPrimaryShiftAction(shift)" class="shift-ui__hint helper">Início liberado em {{ formatDate(shift.date) }}.</p>
          </template>

          <template v-else-if="shiftUiVariant(shift) === 'today'">
            <div class="shift-ui__ribbon">HOJE</div>
            <div class="shift-ui__head shift-ui__head--pad">
              <span class="shift-ui__pill shift-ui__pill--accent">Hoje</span>
            </div>
            <HospitalHeading
              :name="shift.hospitalName"
              :logo-url="shift.hospitalLogoUrl"
              title-class="shift-ui__title shift-ui__title--lg"
            />
            <p class="shift-ui__addr">
              <svg class="shift-ui__ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-4.35 7-11a7 7 0 1 0-14 0c0 6.65 7 11 7 11z" fill="none" stroke="currentColor" stroke-width="1.75" /><circle cx="12" cy="10" r="2.25" fill="none" stroke="currentColor" stroke-width="1.75" /></svg>
              {{ shift.hospitalAddress }}
            </p>
            <div class="shift-ui__divider" />
            <div class="shift-ui__meta-row shift-ui__meta-row--spread">
              <span class="shift-ui__meta">
                <svg class="shift-ui__ico-sm" viewBox="0 0 24 24"><rect x="3.5" y="5.5" width="17" height="15" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3.5 9.5h17M8 3.5v4M16 3.5v4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
                {{ formatWeekdayDayMonthYear(shift.date) }}
              </span>
              <span class="shift-ui__meta shift-ui__meta--with-sep">
                <svg class="shift-ui__ico-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v6l4 2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
                {{ shift.startTime }} - {{ shift.endTime }}
              </span>
              <span class="shift-ui__pay shift-ui__pay--with-sep">{{ mockPayForShift(shift) }}</span>
            </div>
            <div class="shift-ui__actions">
              <button
                v-if="canShowPrimaryShiftAction(shift)"
                type="button"
                class="btn shift-ui__primary"
                @click="openShiftModal(shift)"
              >
                <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M10 8l6 4-6 4V8z" fill="currentColor"/></svg>
                Iniciar agora
              </button>
              <button type="button" class="btn shift-ui__secondary" @click="openMapsForShift(shift)">
                <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 21s7-4.35 7-11a7 7 0 1 0-14 0c0 6.65 7 11 7 11z" fill="none" stroke="currentColor" stroke-width="1.75"/><circle cx="12" cy="10" r="2.25" fill="none" stroke="currentColor" stroke-width="1.75"/></svg>
                Como chegar
              </button>
            </div>
          </template>

          <template v-else-if="shiftUiVariant(shift) === 'active'">
            <div class="shift-ui__ribbon shift-ui__ribbon--green">AO VIVO</div>
            <div class="shift-ui__head shift-ui__head--pad">
              <span class="status" data-status="active">{{ getStatusLabel(shift.status) }}</span>
            </div>
            <HospitalHeading
              :name="shift.hospitalName"
              :logo-url="shift.hospitalLogoUrl"
              title-class="shift-ui__title shift-ui__title--lg"
            />
            <p class="shift-ui__addr">
              <svg class="shift-ui__ico" viewBox="0 0 24 24"><path d="M12 21s7-4.35 7-11a7 7 0 1 0-14 0c0 6.65 7 11 7 11z" fill="none" stroke="currentColor" stroke-width="1.75" /><circle cx="12" cy="10" r="2.25" fill="none" stroke="currentColor" stroke-width="1.75" /></svg>
              {{ shift.hospitalAddress }}
            </p>
            <div class="shift-ui__divider" />
            <div class="shift-ui__active-row">
              <span class="shift-ui__timer">{{ formattedElapsed(shift) }}</span>
              <button type="button" class="btn danger shift-ui__end" @click="openShiftModal(shift)">Encerrar plantão</button>
            </div>
            <button type="button" class="btn shift-ui__secondary full" @click="openMapsForShift(shift)">Como chegar</button>
          </template>

          <template v-else>
            <div class="shift-row">
              <div class="shift-row__title">
                <HospitalHeading
                  :name="shift.hospitalName"
                  :logo-url="shift.hospitalLogoUrl"
                  title-class="shift-ui__title"
                />
              </div>
              <span class="status" :data-status="shift.status">{{ getStatusLabel(shift.status) }}</span>
            </div>
            <p class="shift-ui__addr">{{ shift.hospitalAddress }}</p>
            <p v-if="shift.status !== 'available'" class="shift-ui__elapsed"><strong>Duração:</strong> {{ formattedElapsed(shift) }}</p>

            <div v-if="shift.status === 'completed'" class="log-summary">
              <h4>Resumo de logs</h4>
              <p><strong>Check-in:</strong> {{ formatDateTime(shift.checkIn?.timestamp) }}</p>
              <p><strong>Check-out:</strong> {{ formatDateTime(shift.checkOut?.timestamp) }}</p>
              <p><strong>IP:</strong> {{ shift.checkIn?.ip ?? '-' }}</p>
              <p>
                <strong>Distância check-in:</strong>
                {{ formatDistance(shift.checkIn?.location.distanceToHospitalMeters) }}
              </p>
              <p>
                <strong>Raio 500m:</strong>
                {{ shift.checkIn?.location.within500m ? 'Dentro' : 'Fora' }}
              </p>
              <p><strong>Código imagem:</strong> {{ shift.checkIn?.imageCode ?? '-' }}</p>
            </div>

            <button v-if="shift.status === 'completed'" type="button" class="btn secondary full" @click="openReviewModal(shift)">
              {{ shift.review ? 'Revisão enviada' : 'Mandar para revisão' }}
            </button>
          </template>
        </article>

        <p v-if="shiftsForList.length === 0" class="empty">
          {{
            shiftListSegment === 'completed'
              ? 'Nenhum plantão realizado ainda.'
              : 'Nenhum plantão próximo neste filtro.'
          }}
        </p>
      </section>

      <section v-if="activeTab === 'calendar'" class="list">
        <article class="card calendar-card">
          <div class="calendar-header">
            <button type="button" class="btn ghost small" @click="setCalendarMonth(-1)">Mes anterior</button>
            <h3>{{ calendarMonthLabel }}</h3>
            <button type="button" class="btn ghost small" @click="setCalendarMonth(1)">Proximo mes</button>
          </div>

          <div class="calendar-weekdays">
            <span>Seg</span><span>Ter</span><span>Qua</span><span>Qui</span><span>Sex</span><span>Sab</span><span>Dom</span>
          </div>

          <div class="calendar-grid">
            <button
              v-for="day in calendarDays"
              :key="day.isoDate"
              type="button"
              class="calendar-day"
              :class="{
                muted: !day.isCurrentMonth,
                selected: selectedCalendarDate === day.isoDate,
                marked: hasShiftsInDate(day.isoDate),
              }"
              @click="selectCalendarDate(day.isoDate)"
            >
              <span>{{ day.day }}</span>
              <small v-if="hasShiftsInDate(day.isoDate)">{{ shiftsByDate.get(day.isoDate)?.length }}</small>
            </button>
          </div>

          <div class="calendar-details">
            <h4>Plantões em {{ formatDayMonth(selectedCalendarDate) }}</h4>
            <p v-if="selectedDateShifts.length === 0" class="empty">Nenhum plantão para esta data.</p>
            <div v-else class="calendar-items">
              <div v-for="shift in selectedDateShifts" :key="shift.id" class="calendar-item">
                <div class="calendar-item__main">
                  <HospitalHeading
                    :name="shift.hospitalName"
                    :logo-url="shift.hospitalLogoUrl"
                    compact
                    title-class="calendar-item__hospital"
                  />
                  <span class="calendar-item__time">{{ shift.startTime }} – {{ shift.endTime }}</span>
                </div>
                <span class="status mini" :data-status="shift.status">{{ getStatusLabel(shift.status) }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section v-if="activeTab === 'finance'" class="list">
        <div class="section-heading section-heading--finance">
          <h3 class="section-heading__title">Financeiro</h3>
          <div class="finance-filters">
            <label class="filter-select-wrap">
              <span class="visually-hidden">Filtrar hospital no financeiro</span>
              <select v-model="financeHospitalFilter" class="filter-select filter-select--finance">
                <option value="all">Todos os hospitais</option>
                <option v-for="hospitalName in financeHospitals" :key="hospitalName" :value="hospitalName">
                  {{ hospitalName }}
                </option>
              </select>
            </label>
            <label class="filter-select-wrap">
              <span class="visually-hidden">Filtrar por status no financeiro</span>
              <select v-model="financeStatusFilter" class="filter-select filter-select--finance">
                <option value="all">Todos os status</option>
                <option value="completed">Realizado</option>
                <option value="active">Em andamento</option>
                <option value="available">Pendente</option>
              </select>
            </label>
          </div>
        </div>
        <p class="finance-intro">Resumo dos seus plantões (valores simulados).</p>

        <article class="card finance-dashboard">
          <div class="finance-metrics">
            <div class="finance-metric">
              <span class="finance-metric__label">Plantões</span>
              <span class="finance-metric__value">{{ financeSummary.shiftCount }}</span>
            </div>
            <div class="finance-metric finance-metric--accent">
              <span class="finance-metric__label">A receber</span>
              <span class="finance-metric__value">{{ formatBrl(financeSummary.toReceiveBrl) }}</span>
            </div>
            <div class="finance-metric finance-metric--success">
              <span class="finance-metric__label">Recebido</span>
              <span class="finance-metric__value">{{ formatBrl(financeSummary.receivedBrl) }}</span>
            </div>
          </div>
        </article>

        <article class="card finance-table-card">
          <h4 class="finance-table-title">Plantões detalhados</h4>

          <p v-if="financeShifts.length === 0" class="empty">Nenhum plantão encontrado para este filtro.</p>

          <div v-else class="finance-table-wrap">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Hospital</th>
                  <th>Data</th>
                  <th>Horário</th>
                  <th>Status</th>
                  <th>Tipo</th>
                  <th>Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="shift in financeShifts" :key="`finance-${shift.id}`">
                  <td>{{ shift.hospitalName }}</td>
                  <td>{{ formatDate(shift.date) }}</td>
                  <td>{{ shift.startTime }} - {{ shift.endTime }}</td>
                  <td>{{ getStatusLabel(shift.status) }}</td>
                  <td>
                    {{ shift.status === 'completed' ? 'Recebido' : 'A receber' }}
                  </td>
                  <td class="finance-table__amount">
                    {{ formatBrl(mockPayAmountBrlNumber(shift)) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section v-if="activeTab === 'announcements'" class="list">
        <div class="section-heading">
          <h3 class="section-heading__title">Anúncios</h3>
        </div>
        <p class="finance-intro">Oportunidades extras disponíveis.</p>
        <article v-for="announcement in announcementsVisible" :key="announcement.id" class="card shift-card">
          <div class="shift-row">
            <div class="shift-row__title">
              <HospitalHeading
                :name="announcement.hospitalName"
                :logo-url="announcement.hospitalLogoUrl"
                title-class="announcement-card__title"
              />
            </div>
            <span class="status">Disponivel</span>
          </div>
          <p>{{ announcement.hospitalAddress }}</p>
          <p><strong>Data:</strong> {{ formatDate(announcement.date) }}</p>
          <p><strong>Horario:</strong> {{ announcement.startTime }} - {{ announcement.endTime }}</p>
          <p><strong>Especialidade:</strong> {{ announcement.specialty }}</p>
          <button type="button" class="btn success full" @click="openAnnouncementModal(announcement)">
            Pegar plantao
          </button>
        </article>
        <p v-if="announcementsVisible.length === 0" class="empty">Sem anuncios disponiveis no momento.</p>
      </section>

      <section v-if="activeTab === 'account'" class="list">
        <article class="card shift-card">
          <h3>Conta</h3>
          <p><strong>Medico:</strong> {{ currentDoctor.name }}</p>
          <p><strong>CPF:</strong> {{ currentDoctor.cpf }}</p>
          <button type="button" class="btn ghost full" @click="handleLogout">Sair</button>
        </article>
      </section>

      <nav class="bottom-nav">
        <button type="button" class="bottom-item" :class="{ active: activeTab === 'myShifts' }" @click="activeTab = 'myShifts'">
          <svg class="bottom-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
            <rect x="3.5" y="5.5" width="17" height="15" rx="2.5" fill="none" />
            <path d="M3.5 9.5h17M8 3.5v4M16 3.5v4" />
            <path d="m8.5 14.5 2 2 3.5-3.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>Plantões</span>
        </button>
        <button type="button" class="bottom-item" :class="{ active: activeTab === 'calendar' }" @click="activeTab = 'calendar'">
          <svg class="bottom-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
            <rect x="3.5" y="5.5" width="17" height="15" rx="2.5" />
            <path d="M3.5 9.5h17" />
            <path d="M8 3.5v4" />
            <path d="M16 3.5v4" />
          </svg>
          <span>Agenda</span>
        </button>
        <button type="button" class="bottom-item" :class="{ active: activeTab === 'announcements' }" @click="activeTab = 'announcements'">
          <svg class="bottom-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 11v3a3 3 0 0 0 3 3h2l6 4V4l-6 4H7a3 3 0 0 0-3 3z" />
            <path d="M16 9v6" />
          </svg>
          <span>Anúncios</span>
        </button>
        <!-- Financeiro: oculto no menu por ora; secao activeTab === 'finance' mantida para reativar -->
        <button type="button" class="bottom-item" :class="{ active: activeTab === 'account' }" @click="activeTab = 'account'">
          <svg class="bottom-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="8" r="3.2" />
            <path d="M5 19a7 7 0 0 1 14 0" />
          </svg>
          <span>Conta</span>
        </button>
      </nav>
    </section>
  </main>

  <div v-if="alertsModal.open" class="overlay" role="dialog" aria-modal="true">
    <section class="card modal alert-modal">
      <div class="shift-row">
        <h3>{{ alertsModal.firstAccess ? 'Ativar alertas?' : 'Preferências de alerta' }}</h3>
        <button v-if="!alertsModal.firstAccess" type="button" class="btn ghost small" @click="closeAlertsModal">Fechar</button>
      </div>

      <p class="description">
        {{ alertsModal.firstAccess ? 'No primeiro acesso, escolha se deseja receber avisos de plantão.' : 'Defina se deseja receber notificações antes do início do plantão.' }}
      </p>

      <div class="alert-modal__actions">
        <button type="button" class="btn secondary full" @click="setAlertsPreference(false)">
          {{ alertsModal.firstAccess ? 'Não receber avisos' : 'Inativar alertas' }}
        </button>
        <button type="button" class="btn primary full" @click="setAlertsPreference(true)">
          {{ alertsModal.firstAccess ? 'Receber avisos' : 'Ativar alertas' }}
        </button>
      </div>
    </section>
  </div>

  <div v-if="shiftModal.open" class="overlay" role="dialog" aria-modal="true">
    <section
      class="card modal"
      :class="{ 'modal--shift-summary': shiftModal.step === 'summary' }"
    >
      <template v-if="shiftModal.step === 'summary'">
        <div class="shift-summary-head">
          <p class="shift-summary-head__brand">Humana</p>
          <div class="shift-row shift-summary-head__row">
            <h3 class="shift-summary-head__title">
              {{ shiftModal.mode === 'start' ? 'Resumo do plantão' : 'Encerrar plantão' }}
            </h3>
            <button type="button" class="btn ghost small" @click="closeShiftModal">Fechar</button>
          </div>
        </div>

        <div v-if="selectedShift" class="summary-box summary-box--polished">
          <HospitalHeading
            :name="selectedShift.hospitalName"
            :logo-url="selectedShift.hospitalLogoUrl"
            title-class="summary-box__hospital-title"
          />
          <dl class="summary-deflist">
            <div class="summary-deflist__row">
              <dt>Endereço</dt>
              <dd>{{ selectedShift.hospitalAddress }}</dd>
            </div>
            <div class="summary-deflist__row">
              <dt>Data</dt>
              <dd>{{ formatDate(selectedShift.date) }}</dd>
            </div>
            <div class="summary-deflist__row">
              <dt>Horário</dt>
              <dd>{{ selectedShift.startTime }} – {{ selectedShift.endTime }}</dd>
            </div>
          </dl>
        </div>

        <button
          type="button"
          class="btn giant-round shift-summary-cta"
          :class="shiftModal.mode === 'start' ? 'success' : 'danger'"
          @click="proceedToCheckModal"
        >
          {{ shiftModal.mode === 'start' ? 'INICIAR PLANTÃO' : 'ENCERRAR PLANTÃO' }}
        </button>
      </template>

      <template v-else>
        <div class="shift-row">
          <h3>{{ shiftModal.mode === 'start' ? 'Confirmar inicio' : 'Confirmar encerramento' }}</h3>
          <div class="row-actions">
            <button type="button" class="btn ghost small" @click="shiftModal.step = 'summary'">Voltar</button>
            <button type="button" class="btn ghost small" @click="closeShiftModal">Fechar</button>
          </div>
        </div>

        <p class="helper">
          Ao abrir este passo, o navegador deve mostrar o pedido de permissao de localizacao.
        </p>

        <div v-if="shiftModal.mode === 'start'" class="camera-box">
          <video
            v-if="!shiftModal.imageDataUrl"
            ref="cameraVideoRef"
            class="camera-preview"
            autoplay
            playsinline
            muted
          />
          <img
            v-else
            :src="shiftModal.imageDataUrl"
            alt="Registro do check-in"
            class="camera-preview"
          />

          <button
            v-if="!shiftModal.imageDataUrl"
            type="button"
            class="btn primary full big giant-action"
            :disabled="shiftModal.isStartingCamera"
            @click="capturePhotoFromCamera"
          >
            {{ shiftModal.isStartingCamera ? 'Abrindo câmera...' : '📷  Tirar foto' }}
          </button>

          <button
            v-else
            type="button"
            class="btn ghost full"
            @click="retakePhoto"
          >
            Tirar novamente
          </button>
        </div>
        <p v-if="shiftModal.cameraError" class="helper error">{{ shiftModal.cameraError }}</p>

        <div class="location-box">
          <p v-if="shiftModal.isCollectingContext" class="helper">📍 Obtendo localização...</p>
          <template v-else-if="shiftModal.location">
            <p v-if="shiftModal.location.distanceToHospitalMeters > 0">
              <!-- TODO: bloquear check-in fora de 500m quando geofence estiver ativo -->
              📍 Você está a <strong>{{ formatDistance(shiftModal.location.distanceToHospitalMeters) }}</strong> do plantão
              <span v-if="shiftModal.location.within500m"> ✅</span>
              <span v-else> — fora do raio do hospital</span>
            </p>
            <p v-else class="helper">📍 Localização registrada</p>
          </template>
          <p v-else-if="shiftModal.locationError" class="helper">
            📍 Localização não disponível
            <button type="button" class="btn ghost small" style="margin-left:0.5rem" @click="collectRuntimeContext">Tentar novamente</button>
          </p>
        </div>

        <p v-if="shiftModal.formError" class="helper error">{{ shiftModal.formError }}</p>

        <button type="button" class="btn primary full big" @click="confirmShiftAction">
          {{ shiftModal.mode === 'start' ? 'Registrar inicio' : 'Registrar encerramento' }}
        </button>
      </template>
    </section>
  </div>

  <div v-if="reviewModal.open" class="overlay" role="dialog" aria-modal="true">
    <section class="card modal">
      <div class="shift-row">
        <h3>Enviar para revisao</h3>
        <button type="button" class="btn ghost small" @click="closeReviewModal">Fechar</button>
      </div>

      <div v-if="selectedReviewShift" class="review-modal__plantao">
        <span class="review-modal__plantao-label">Plantão</span>
        <HospitalHeading
          :name="selectedReviewShift.hospitalName"
          :logo-url="selectedReviewShift.hospitalLogoUrl"
          compact
          as="span"
          title-class="review-modal__hospital-name"
        />
      </div>
      <label for="review-message" class="label">Mensagem para revisao</label>
      <textarea id="review-message" v-model="reviewModal.text" class="textarea" rows="5" />
      <p v-if="reviewModal.error" class="helper error">{{ reviewModal.error }}</p>
      <button type="button" class="btn primary full" @click="submitReview">Enviar revisao</button>
    </section>
  </div>

  <div v-if="announcementModal.open" class="overlay" role="dialog" aria-modal="true">
    <section class="card modal modal--shift-summary">
      <div class="shift-row">
        <h3>Confirmar plantao</h3>
        <button type="button" class="btn ghost small" @click="closeAnnouncementModal">Fechar</button>
      </div>
      <div v-if="selectedAnnouncement" class="summary-box summary-box--polished">
        <HospitalHeading
          :name="selectedAnnouncement.hospitalName"
          :logo-url="selectedAnnouncement.hospitalLogoUrl"
          title-class="summary-box__hospital-title"
        />
        <dl class="summary-deflist">
          <div class="summary-deflist__row">
            <dt>Endereço</dt>
            <dd>{{ selectedAnnouncement.hospitalAddress }}</dd>
          </div>
          <div class="summary-deflist__row">
            <dt>Data</dt>
            <dd>{{ formatDate(selectedAnnouncement.date) }}</dd>
          </div>
          <div class="summary-deflist__row">
            <dt>Horário</dt>
            <dd>{{ selectedAnnouncement.startTime }} – {{ selectedAnnouncement.endTime }}</dd>
          </div>
          <div class="summary-deflist__row">
            <dt>Especialidade</dt>
            <dd>{{ selectedAnnouncement.specialty }}</dd>
          </div>
        </dl>
      </div>
      <p class="helper">Deseja mesmo pegar este plantao? Ele sera adicionado em Meus plantoes e Calendario.</p>
      <button type="button" class="btn success full big" @click="takeAnnouncementShift">Confirmar e pegar plantao</button>
    </section>
  </div>
</template>
