/**
 * Catálogo de Produtos e Categorias
 * Frontend JavaScript - Grupo 2
 * Serviços de Redes para Internet
 */

const API_BASE = '/api';

// ============================================
// NAVEGAÇÃO POR ABAS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Configurar tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            // Atualizar abas ativas
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Atualizar seções visíveis
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(`section-${target}`).classList.add('active');
        });
    });

    // Fechar modal ao clicar fora
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });

    // Fechar modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
        }
    });

    // Carregar dados iniciais
    carregarCategorias();
    carregarProdutos();
});

// ============================================
// UTILITÁRIOS
// ============================================

function mostrarToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;

    const icones = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icones[tipo] || ''}</span> ${mensagem}`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function abrirModal(id) {
    document.getElementById(id).classList.add('active');
}

function fecharModal(id) {
    document.getElementById(id).classList.remove('active');
}

function formatarPreco(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function classificarEstoque(qtd) {
    if (qtd <= 5) return 'low';
    if (qtd <= 20) return 'medium';
    return 'high';
}

function truncar(texto, max = 60) {
    if (!texto) return '—';
    return texto.length > max ? texto.substring(0, max) + '...' : texto;
}

// ============================================
// CATEGORIAS
// ============================================

let categorias = [];

async function carregarCategorias() {
    try {
        const response = await fetch(`${API_BASE}/categorias/`);
        if (!response.ok) throw new Error('Erro ao carregar categorias');

        categorias = await response.json();
        renderizarCategorias();
        atualizarSelectsCategorias();
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('Erro ao carregar categorias', 'error');
    }
}

function renderizarCategorias() {
    const tbody = document.getElementById('tbody-categorias');

    if (categorias.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <div class="empty-icon">📭</div>
                    <p>Nenhuma categoria cadastrada</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = categorias.map(cat => `
        <tr>
            <td><strong>#${cat.id}</strong></td>
            <td>${cat.nome}</td>
            <td>${truncar(cat.descricao)}</td>
            <td>
                <div class="actions-cell">
                    <button class="btn-icon" title="Editar" onclick="editarCategoria(${cat.id})">✏️</button>
                    <button class="btn-icon danger" title="Excluir" onclick="confirmarExcluirCategoria(${cat.id}, '${cat.nome}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function atualizarSelectsCategorias() {
    const options = categorias.map(cat =>
        `<option value="${cat.id}">${cat.nome}</option>`
    ).join('');

    // Select do filtro
    const filtro = document.getElementById('filtro-categoria');
    const filtroAtual = filtro.value;
    filtro.innerHTML = `<option value="">Todas as categorias</option>${options}`;
    filtro.value = filtroAtual;

    // Select do formulário de produto
    const select = document.getElementById('produto-categoria');
    const selectAtual = select.value;
    select.innerHTML = `<option value="">Selecione uma categoria</option>${options}`;
    select.value = selectAtual;
}

function abrirModalCategoria() {
    document.getElementById('modal-categoria-titulo').textContent = 'Nova Categoria';
    document.getElementById('form-categoria').reset();
    document.getElementById('categoria-id').value = '';
    abrirModal('modal-categoria');
}

function editarCategoria(id) {
    const cat = categorias.find(c => c.id === id);
    if (!cat) return;

    document.getElementById('modal-categoria-titulo').textContent = 'Editar Categoria';
    document.getElementById('categoria-id').value = cat.id;
    document.getElementById('categoria-nome').value = cat.nome;
    document.getElementById('categoria-descricao').value = cat.descricao || '';
    abrirModal('modal-categoria');
}

async function salvarCategoria(event) {
    event.preventDefault();

    const id = document.getElementById('categoria-id').value;
    const dados = {
        nome: document.getElementById('categoria-nome').value.trim(),
        descricao: document.getElementById('categoria-descricao').value.trim() || null,
    };

    try {
        const url = id
            ? `${API_BASE}/categorias/${id}`
            : `${API_BASE}/categorias/`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erro ao salvar categoria');
        }

        fecharModal('modal-categoria');
        mostrarToast(
            id ? 'Categoria atualizada com sucesso!' : 'Categoria criada com sucesso!',
            'success'
        );
        carregarCategorias();
        carregarProdutos();
    } catch (error) {
        mostrarToast(error.message, 'error');
    }
}

function confirmarExcluirCategoria(id, nome) {
    document.getElementById('confirmar-mensagem').textContent =
        `Tem certeza que deseja excluir a categoria "${nome}"? Todos os produtos desta categoria também serão removidos.`;

    const btnConfirmar = document.getElementById('btn-confirmar-excluir');
    btnConfirmar.onclick = () => excluirCategoria(id);

    abrirModal('modal-confirmar');
}

async function excluirCategoria(id) {
    try {
        const response = await fetch(`${API_BASE}/categorias/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Erro ao excluir categoria');

        fecharModal('modal-confirmar');
        mostrarToast('Categoria excluída com sucesso!', 'success');
        carregarCategorias();
        carregarProdutos();
    } catch (error) {
        mostrarToast(error.message, 'error');
    }
}

// ============================================
// PRODUTOS
// ============================================

let produtos = [];

async function carregarProdutos() {
    try {
        const filtro = document.getElementById('filtro-categoria').value;
        const params = filtro ? `?categoria_id=${filtro}` : '';
        const response = await fetch(`${API_BASE}/produtos/${params}`);
        if (!response.ok) throw new Error('Erro ao carregar produtos');

        produtos = await response.json();
        renderizarProdutos();
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('Erro ao carregar produtos', 'error');
    }
}

function renderizarProdutos() {
    const tbody = document.getElementById('tbody-produtos');

    if (produtos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <div class="empty-icon">📭</div>
                    <p>Nenhum produto cadastrado</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = produtos.map(prod => `
        <tr>
            <td><strong>#${prod.id}</strong></td>
            <td>${prod.nome}</td>
            <td>${truncar(prod.descricao)}</td>
            <td class="price">${formatarPreco(prod.preco)}</td>
            <td>
                <span class="stock ${classificarEstoque(prod.estoque)}">${prod.estoque}</span>
            </td>
            <td>
                <span class="badge">${prod.categoria ? prod.categoria.nome : '—'}</span>
            </td>
            <td>
                <div class="actions-cell">
                    <button class="btn-icon" title="Editar" onclick="editarProduto(${prod.id})">✏️</button>
                    <button class="btn-icon danger" title="Excluir" onclick="confirmarExcluirProduto(${prod.id}, '${prod.nome.replace(/'/g, "\\'")}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function abrirModalProduto() {
    if (categorias.length === 0) {
        mostrarToast('Cadastre pelo menos uma categoria antes de adicionar produtos', 'info');
        return;
    }

    document.getElementById('modal-produto-titulo').textContent = 'Novo Produto';
    document.getElementById('form-produto').reset();
    document.getElementById('produto-id').value = '';
    document.getElementById('produto-estoque').value = '0';
    abrirModal('modal-produto');
}

function editarProduto(id) {
    const prod = produtos.find(p => p.id === id);
    if (!prod) return;

    document.getElementById('modal-produto-titulo').textContent = 'Editar Produto';
    document.getElementById('produto-id').value = prod.id;
    document.getElementById('produto-nome').value = prod.nome;
    document.getElementById('produto-descricao').value = prod.descricao || '';
    document.getElementById('produto-preco').value = prod.preco;
    document.getElementById('produto-estoque').value = prod.estoque;
    document.getElementById('produto-categoria').value = prod.categoria_id;
    abrirModal('modal-produto');
}

async function salvarProduto(event) {
    event.preventDefault();

    const id = document.getElementById('produto-id').value;
    const dados = {
        nome: document.getElementById('produto-nome').value.trim(),
        descricao: document.getElementById('produto-descricao').value.trim() || null,
        preco: parseFloat(document.getElementById('produto-preco').value),
        estoque: parseInt(document.getElementById('produto-estoque').value, 10),
        categoria_id: parseInt(document.getElementById('produto-categoria').value, 10),
    };

    try {
        const url = id
            ? `${API_BASE}/produtos/${id}`
            : `${API_BASE}/produtos/`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erro ao salvar produto');
        }

        fecharModal('modal-produto');
        mostrarToast(
            id ? 'Produto atualizado com sucesso!' : 'Produto criado com sucesso!',
            'success'
        );
        carregarProdutos();
    } catch (error) {
        mostrarToast(error.message, 'error');
    }
}

function confirmarExcluirProduto(id, nome) {
    document.getElementById('confirmar-mensagem').textContent =
        `Tem certeza que deseja excluir o produto "${nome}"?`;

    const btnConfirmar = document.getElementById('btn-confirmar-excluir');
    btnConfirmar.onclick = () => excluirProduto(id);

    abrirModal('modal-confirmar');
}

async function excluirProduto(id) {
    try {
        const response = await fetch(`${API_BASE}/produtos/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Erro ao excluir produto');

        fecharModal('modal-confirmar');
        mostrarToast('Produto excluído com sucesso!', 'success');
        carregarProdutos();
    } catch (error) {
        mostrarToast(error.message, 'error');
    }
}
