const fs = require('fs');
const path = require('path');

const REPORT = path.join(__dirname, 'public', 'relatorio-funcionalidades.html');
let html = fs.readFileSync(REPORT, 'utf8');

// Mapeia: [arquivo, label no placeholder]
const replacements = [
  ['login.png',        'Screenshot: Tela de Login'],
  ['indicator.png',    'Screenshot: Dashboard de Indicadores'],
  ['dashboard.png',    'Screenshot: Home / Dashboard'],
  ['payments.png',     'Screenshot: Módulo de Pagamentos'],
  ['financial.png',    'Screenshot: Relatório Financeiro'],
  ['planning.png',     'Screenshot: Módulo Planejado'],
  ['completed.png',    'Screenshot: Plantões Realizados'],
  ['timesheet.png',    'Screenshot: Fechamento de Ponto'],
  ['import-batch.png', 'Screenshot: Status das Importações'],
  ['pending.png',      'Screenshot: Análise de Pendências'],
  ['report.png',       'Screenshot: Módulo de Relatórios'],
  ['wallet.png',       'Screenshot: Carteira de Profissionais'],
  ['professionals.png','Screenshot: Lista de Profissionais'],
  ['personal-data.png','Screenshot: Dados Pessoais do Profissional'],
  ['prof-info.png',    'Screenshot: Informações Profissionais'],
  ['attachments.png',  'Screenshot: Documentos e Anexos'],
  ['locals.png',       'Screenshot: Locais e Setores'],
  ['user.png',         'Screenshot: Gestão de Usuários'],
  ['profile.png',      'Screenshot: Meu Perfil'],
  ['financial.png',    'Screenshot: Modal de Lançamento'],
  ['timesheet.png',    'Screenshot: Modal de Importação'],
  ['timesheet.png',    'Screenshot: Modal de Fechamento'],
];

let count = 0;
for (const [file, label] of replacements) {
  const imgHTML = `<div class="screenshot-box" style="padding:0;min-height:auto;background:#000;border:2px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:20px;">
    <img src="screenshots/${file}" alt="${label}" style="width:100%;display:block;border-radius:6px;" />
  </div>`;

  // Regex flexível para capturar o bloco da screenshot-box com esse label
  const re = new RegExp(
    `<div class="screenshot-box">\\s*<div class="ph-icon">[^<]*<\\/div>\\s*<div class="ph-label">${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}<\\/div>[\\s\\S]*?<\\/div>`,
    ''
  );
  const before = html;
  html = html.replace(re, imgHTML);
  if (html !== before) count++;
}

fs.writeFileSync(REPORT, html);
console.log('Substituições feitas:', count);
