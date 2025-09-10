// Matrix Form — JS
// - Animação de code rain (canvas)
// - UX do formulário: contador, validação amigável, persistência local

const $ = (sel, ctx = document) => ctx.querySelector(sel);

// ------------------ Utilidades ------------------
const storage = {
  get(key, fallback = null) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
  },
  del(key) {
    try { localStorage.removeItem(key); } catch {}
  }
};

// ------------------ Code rain ------------------
function startMatrixRain() {
  const canvas = document.getElementById('matrix-rain');
  if (!canvas) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return; // respeita usuários que preferem menos movimento

  const ctx = canvas.getContext('2d');
  const chars = '01C6	F9513'; // majoritariamente 0/1 com alguns códigos estranhos para vibe
  const fontSize = 16;
  let columns;
  let drops;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    columns = Math.floor(canvas.width / fontSize);
    drops = Array(columns).fill(1 + Math.random() * canvas.height / fontSize);
  }

  function draw() {
    // cria o efeito de trilha
    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff41';
    ctx.font = `${fontSize}px "Share Tech Mono", monospace`;

    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;
      ctx.fillText(char, x, y);
      // reset aleatório após sair da tela
      if (y > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
}

// ------------------ Formulário ------------------
function setupForm() {
  const form = document.getElementById('form-recrutamento');
  if (!form) return;

  const nome = $('#nome', form);
  const email = $('#email', form);
  const senha = $('#senha', form);
  const pais = $('#pais', form);
  const mensagem = $('#mensagem', form);
  const count = $('#count');
  const feedback = $('#feedback');

  // hidrata com valores salvos
  const saved = storage.get('matrix-form');
  if (saved) {
    for (const [k, v] of Object.entries(saved)) {
      if (form.elements[k]) form.elements[k].value = v;
    }
    if (mensagem && saved.mensagem) count.textContent = String(saved.mensagem.length);
  }

  // contador de caracteres
  mensagem?.addEventListener('input', () => {
    count.textContent = String(mensagem.value.length);
    persist();
  });

  // persistência leve
  form.addEventListener('input', persist);
  function persist() {
    const data = Object.fromEntries(new FormData(form));
    storage.set('matrix-form', data);
  }

  // reset limpa storage e feedback
  form.addEventListener('reset', () => {
    storage.del('matrix-form');
    count.textContent = '0';
    setTimeout(() => feedback.textContent = '', 0);
  });

  // envio com validação amigável
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    feedback.textContent = '';

    if (!form.checkValidity()) {
      form.reportValidity();
      feedback.textContent = 'Confira os campos destacados e tente novamente.';
      feedback.style.borderColor = 'rgba(255,64,96,0.6)';
      feedback.style.background = 'rgba(255,64,96,0.08)';
      return;
    }

    // sucesso: pequena mensagem personalizada
    const firstName = (nome?.value || '').split(' ')[0] || 'Operador';
    feedback.textContent = `Acesso concedido, ${firstName}. Um operador entrará em contato por e‑mail.`;
    feedback.style.borderColor = 'rgba(0,255,65,0.35)';
    feedback.style.background = 'rgba(0,255,65,0.07)';

    // Mantém dados locais por conveniência; comente caso não queira
    // storage.del('matrix-form');
  });
}

// ------------------ Inicialização ------------------
document.addEventListener('DOMContentLoaded', () => {
  startMatrixRain();
  setupForm();
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
});

