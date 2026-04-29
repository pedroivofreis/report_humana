# Humana Check-in Lite

MVP PWA (mock) para fluxo de check-in medico.

## Stack

- Vue 3
- TypeScript
- Vite

## Fluxo implementado (mock)

- Login por CPF (validacao local mock).
- Aba de plantoes disponiveis.
- Modal de iniciar/encerrar plantao.
- Captura de foto (camera/galeria), codigo da imagem (hash SHA-256), localizacao e IP.
- Verificacao de distancia para hospital (raio de 500m) e registro em log.
- Cronometro durante plantao em andamento.
- Aba de plantoes realizados com resumo de logs.
- Envio para revisao com texto.
- Aba de calendario com os plantoes por data.

## Rodar local

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## CPFs de teste

- `11122233344`
- `55566677788`

## Nota

- Ajustes visuais e de fluxo mobile/PWA seguem em evolução via PR.
