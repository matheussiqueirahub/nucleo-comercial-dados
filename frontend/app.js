const toast = document.getElementById("toast");
const themeToggle = document.getElementById("toggle-theme");

const api = {
  async get(path) {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json();
  },
  async post(path, payload) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.status === 204 ? null : response.json();
  },
  async patch(path, payload) {
    const response = await fetch(path, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json();
  },
  async delete(path) {
    const response = await fetch(path, { method: "DELETE" });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  },
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3200);
}

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

function formatDate(iso) {
  return new Date(iso).toLocaleString("pt-BR");
}

async function carregarIndicadores() {
  const [produtos, receita, vendas, baixo] = await Promise.all([
    api.get("/produtos"),
    api.get("/relatorios/receita"),
    api.get("/vendas"),
    api.get("/relatorios/estoque_baixo"),
  ]);

  document.getElementById("stat-produtos").textContent = produtos.length;
  document.getElementById("stat-receita").textContent = formatCurrency(
    receita.receita || 0
  );
  document.getElementById("stat-vendas").textContent = vendas.length;
  document.getElementById("stat-baixo").textContent = baixo.length;
}

function renderProdutos(produtos) {
  const lista = document.getElementById("lista-produtos");
  lista.innerHTML = "";

  produtos.forEach((produto) => {
    const row = document.createElement("div");
    row.className = "table__row";
    row.innerHTML = `
      <span>${produto.nome}</span>
      <span>${produto.quantidade_disponivel}</span>
      <span>${formatCurrency(produto.preco)}</span>
      <span>
        <span class="status ${
          produto.ativo ? "status--active" : "status--inactive"
        }">
          ${produto.ativo ? "Ativo" : "Inativo"}
        </span>
      </span>
    `;
    lista.appendChild(row);
  });
}

function renderVendas(vendas) {
  const lista = document.getElementById("lista-vendas");
  lista.innerHTML = "";
  vendas.slice(0, 6).forEach((venda) => {
    const row = document.createElement("div");
    row.className = "table__row";
    row.innerHTML = `
      <span>#${venda.id}</span>
      <span>${venda.produto_id}</span>
      <span>${venda.quantidade}</span>
      <span>${formatDate(venda.data_venda)}</span>
    `;
    lista.appendChild(row);
  });
}

function renderEstoqueBaixo(itens) {
  const lista = document.getElementById("lista-baixo");
  lista.innerHTML = "";
  if (!itens.length) {
    lista.innerHTML = "<p class='muted'>Nenhum item crítico.</p>";
    return;
  }

  itens.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <strong>${item.nome}</strong>
      <p class="muted">${item.descricao || "Sem descrição"}</p>
      <p>Estoque: <strong>${item.quantidade_disponivel}</strong></p>
    `;
    lista.appendChild(card);
  });
}

async function carregarDashboard() {
  const [produtos, vendas, baixo] = await Promise.all([
    api.get("/produtos?incluir_inativos=true"),
    api.get("/vendas"),
    api.get("/relatorios/estoque_baixo"),
  ]);
  renderProdutos(produtos);
  renderVendas(vendas);
  renderEstoqueBaixo(baixo);
  await carregarIndicadores();
}

document.getElementById("refresh").addEventListener("click", async () => {
  await carregarDashboard();
  showToast("Dados atualizados.");
});

document.getElementById("busca-produto").addEventListener("input", async (e) => {
  const termo = e.target.value.trim();
  const produtos = await api.get(
    `/produtos${termo ? `?q=${encodeURIComponent(termo)}` : ""}`
  );
  renderProdutos(produtos);
});

document.getElementById("form-produto").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  const payload = {
    nome: data.get("nome"),
    descricao: data.get("descricao"),
    quantidade_disponivel: Number(data.get("quantidade")),
    preco: Number(data.get("preco")),
  };
  await api.post("/produtos", payload);
  e.target.reset();
  showToast("Produto cadastrado.");
  await carregarDashboard();
});

document.getElementById("form-venda").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  const payload = {
    produto_id: Number(data.get("produto_id")),
    quantidade: Number(data.get("quantidade")),
  };
  await api.post("/vendas", payload);
  e.target.reset();
  showToast("Venda registrada.");
  await carregarDashboard();
});

document.getElementById("form-estoque").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  const produtoId = Number(data.get("produto_id"));
  const payload = { delta: Number(data.get("delta")) };
  await api.post(`/produtos/${produtoId}/estoque`, payload);
  e.target.reset();
  showToast("Estoque ajustado.");
  await carregarDashboard();
});

document
  .getElementById("form-atualizar")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const produtoId = Number(data.get("produto_id"));
    const payload = {
      nome: data.get("nome") || null,
      descricao: data.get("descricao") || null,
      quantidade_disponivel: data.get("quantidade")
        ? Number(data.get("quantidade"))
        : null,
      preco: data.get("preco") ? Number(data.get("preco")) : null,
    };
    await api.patch(`/produtos/${produtoId}`, payload);
    e.target.reset();
    showToast("Produto atualizado.");
    await carregarDashboard();
  });

document.querySelectorAll("[data-report]").forEach((button) => {
  button.addEventListener("click", async () => {
    const tipo = button.dataset.report;
    const output = document.getElementById("relatorio-output");
    output.textContent = "Carregando...";
    if (tipo === "receita") {
      const receita = await api.get("/relatorios/receita");
      output.textContent = `Receita total: ${formatCurrency(receita.receita)}`;
      return;
    }
    if (tipo === "ranking") {
      const ranking = await api.get("/relatorios/ranking");
      output.innerHTML = ranking
        .map(
          (item) =>
            `${item.nome}: ${item.total_vendido} un. (${formatCurrency(
              item.receita
            )})`
        )
        .join("<br />");
      return;
    }
    if (tipo === "giro") {
      const giro = await api.get("/relatorios/giro");
      output.innerHTML = giro
        .slice(0, 6)
        .map(
          (item) =>
            `${item.nome}: média ${item.media_diaria_vendida} / dia`
        )
        .join("<br />");
      return;
    }
    const baixo = await api.get("/relatorios/estoque_baixo");
    output.innerHTML = baixo
      .map(
        (item) =>
          `${item.nome}: ${item.quantidade_disponivel} un. em estoque`
      )
      .join("<br />");
  });
});

themeToggle.addEventListener("click", () => {
  const theme = document.body.dataset.theme === "dark" ? "light" : "dark";
  document.body.dataset.theme = theme === "dark" ? "dark" : "light";
  showToast(`Tema ${theme === "dark" ? "escuro" : "claro"} ativado.`);
});

carregarDashboard().catch((error) => {
  console.error(error);
  showToast("Erro ao carregar dados da API.");
});
