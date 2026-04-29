<script setup lang="ts">
withDefaults(
  defineProps<{
    name: string
    /** Quando existir (ex.: URL da API), substitui o ícone padrão. */
    logoUrl?: string
    /** Classes aplicadas ao título (ex.: `shift-ui__title`). */
    titleClass?: string
    /** Linha compacta (banner, calendário, barra ativa). */
    compact?: boolean
    as?: 'h2' | 'h3' | 'h4' | 'p' | 'span'
  }>(),
  {
    compact: false,
    as: 'h3',
  },
)
</script>

<template>
  <div class="hospital-heading" :class="{ 'hospital-heading--compact': compact }">
    <div class="hospital-heading__badge" aria-hidden="true">
      <img
        v-if="logoUrl"
        :src="logoUrl"
        alt=""
        class="hospital-heading__logo"
        decoding="async"
      />
      <svg
        v-else
        class="hospital-heading__icon"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M4 21V10l8-5 8 5v11M9 21v-4h6v4M12 7v3m0 0v3m0-3h3m-3 0H9"
        />
      </svg>
    </div>
    <component :is="as" class="hospital-heading__title" :class="titleClass">
      {{ name }}
    </component>
  </div>
</template>

<style scoped>
.hospital-heading {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  min-width: 0;
}

.hospital-heading--compact {
  gap: 0.35rem;
  align-items: center;
}

.hospital-heading__badge {
  flex-shrink: 0;
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 10px;
  background: linear-gradient(145deg, var(--primary-soft, #fff1eb) 0%, #ffe8dc 100%);
  border: 1.5px solid rgba(246, 81, 17, 0.22);
  display: grid;
  place-items: center;
  overflow: hidden;
}

.hospital-heading--compact .hospital-heading__badge {
  width: 1.7rem;
  height: 1.7rem;
  border-radius: 8px;
}

.hospital-heading__logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 0.15rem;
}

.hospital-heading__icon {
  width: 1.15rem;
  height: 1.15rem;
  color: var(--primary-dark, #d9450e);
}

.hospital-heading--compact .hospital-heading__icon {
  width: 0.95rem;
  height: 0.95rem;
}

.hospital-heading__title {
  margin: 0;
  min-width: 0;
}
</style>
