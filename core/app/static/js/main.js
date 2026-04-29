document.addEventListener("DOMContentLoaded", function() {
    
    const formExtracao = document.getElementById('form-extracao');
    const inputArquivos = document.getElementById('arquivos');
    const areaProgresso = document.getElementById('area-progresso');
    const barra = document.getElementById('barra');
    const statusTexto = document.getElementById('status-texto');
    const areaPlanilha = document.getElementById('area-planilha');


    if (formExtracao) {
        formExtracao.addEventListener('submit', async function(e) {
            e.preventDefault();
            const arquivos = inputArquivos.files;

            if (arquivos.length === 0) {
                alert("Selecione pelo menos um arquivo.");
                return;
            }

            iniciarProgresso();

            for (let i = 0; i < arquivos.length; i++) {
                statusTexto.innerText = `Lendo arquivo ${i + 1} de ${arquivos.length}: ${arquivos[i].name}...`;
                
                const formData = new FormData();
                formData.append('certificado', arquivos[i]);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

                await enviarParaServidor(formData);
                atualizarBarra(i + 1, arquivos.length);
            }

            finalizarProcesso();
        });
    }

    const modalCertificados = document.getElementById('modalCertificados');
    
    if (modalCertificados) {
        // Quando o modal abre, busca os arquivos pendentes
        modalCertificados.addEventListener('show.bs.modal', function () {
            const listaContainer = document.getElementById('lista-certificados-modal');
            listaContainer.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Carregando seus arquivos...</p></div>';

            fetch('/listar-certificados-novos/')
                .then(response => response.json())
                .then(data => {
                    listaContainer.innerHTML = '';
                    if (data.certificados.length === 0) {
                        listaContainer.innerHTML = '<div class="p-4 text-center text-muted">Nenhum arquivo pendente de processamento.</div>';
                        return;
                    }
                    
                    data.certificados.forEach(c => {
                        listaContainer.innerHTML += `
                            <label class="list-group-item list-group-item-action d-flex align-items-center gap-3 cursor-pointer">
                                <input class="form-check-input flex-shrink-0" type="checkbox" name="cert_id_modal" value="${c.id}" data-nome="${c.nome}">
                                <div class="text-truncate">
                                    <i class="bi bi-file-earmark-pdf-fill text-danger me-2"></i>${c.nome}
                                </div>
                            </label>
                        `;
                    });
                })
                .catch(err => {
                    listaContainer.innerHTML = '<div class="p-4 text-center text-danger">Erro ao carregar arquivos.</div>';
                });
        });

        // Quando clica no botão "Processar Selecionados" do modal
        document.getElementById('btn-confirmar-modal').addEventListener('click', async function() {
            const selecionados = document.querySelectorAll('input[name="cert_id_modal"]:checked');
            
            if (selecionados.length === 0) {
                alert("Selecione pelo menos um arquivo.");
                return;
            }

            // Fecha o modal do Bootstrap
            const modalInstance = bootstrap.Modal.getInstance(modalCertificados);
            modalInstance.hide();

            iniciarProgresso();

            for (let i = 0; i < selecionados.length; i++) {
                const id = selecionados[i].value;
                const nome = selecionados[i].getAttribute('data-nome');
                
                statusTexto.innerText = `Processando arquivo salvo ${i + 1} de ${selecionados.length}: ${nome}...`;
                
                const formData = new FormData();
                formData.append('id_existente', id);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

                await enviarParaServidor(formData);
                atualizarBarra(i + 1, selecionados.length);
            }

            finalizarProcesso();
        });
    }

    function iniciarProgresso() {
        areaProgresso.style.display = 'block';
        areaPlanilha.style.display = 'none';
        barra.style.width = '0%';
        barra.innerText = '0%';
        barra.classList.remove('bg-danger');
        barra.classList.add('bg-success');
    }

    function atualizarBarra(atual, total) {
        let percent = Math.round((atual / total) * 100);
        barra.style.width = percent + '%';
        barra.innerText = percent + '%';
    }

    async function enviarParaServidor(formData) {
        try {
            const response = await fetch('/processar-arquivo/', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (!response.ok) {
                console.error("Erro na IA:", data.erro);
            }
            return data;
        } catch (error) {
            console.error("Erro de requisição:", error);
        }
    }

    function finalizarProcesso() {
        statusTexto.innerText = "Processamento concluído!";
        barra.classList.remove('progress-bar-animated');
        areaPlanilha.style.display = 'block';
    }
});