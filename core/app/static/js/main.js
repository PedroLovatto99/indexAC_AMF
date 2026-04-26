document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-indexac');
    const inputArquivos = document.getElementById('arquivos');
    const inputNome = document.getElementById('nome');
    const inputCurso = document.getElementById('curso');
    
    const btnGerar = document.getElementById('btn-gerar');
    const progressoContainer = document.getElementById('progresso-container');
    const barra = document.getElementById('barra');
    const statusTexto = document.getElementById('status-texto');
    const downloadArea = document.getElementById('download-area');
    const linkDownload = document.getElementById('link-download');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const arquivos = inputArquivos.files;
        const nome = inputNome.value;
        const curso = inputCurso.value;
        
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        
        progressoContainer.style.display = 'block';
        downloadArea.style.display = 'none';
        btnGerar.disabled = true;

        for (let i = 0; i < arquivos.length; i++) {
            
            let percentual = ((i + 1) / arquivos.length) * 100;
            barra.style.width = percentual + '%';
            statusTexto.innerText = `Analisando certificado ${i+1} de ${arquivos.length}...`;

            const formData = new FormData();
            formData.append('certificado', arquivos[i]);
            formData.append('nome', nome);
            formData.append('curso', curso);

            try {
                const response = await fetch('/processar-arquivo/', {
                    method: 'POST',
                    body: formData,
                    headers: { 
                        'X-CSRFToken': csrfToken
                    }
                });

                if (!response.ok) {
                    console.error(`Erro ao processar arquivo ${arquivos[i].name}`);
                }
            } catch (error) {
                console.error("Erro na requisição:", error);
            }
        }

        statusTexto.innerText = "Concluído! Gerando sua planilha...";
        barra.classList.remove('progress-bar-animated');
        barra.classList.add('bg-success');

        try {
            const responseFinal = await fetch(`/gerar-planilha/?nome=${encodeURIComponent(nome)}&curso=${encodeURIComponent(curso)}`);
            
            if (responseFinal.ok) {
                const blob = await responseFinal.blob();
                const url = window.URL.createObjectURL(blob);
                
                linkDownload.href = url;
                linkDownload.download = `Horas Complementares.xlsx`;
                
                downloadArea.style.display = 'block';
                statusTexto.innerText = "Planilha pronta para download!";
            } else {
                statusTexto.innerText = "Erro ao gerar a planilha final.";
                statusTexto.classList.add('text-danger');
            }
        } catch (error) {
            console.error("Erro ao baixar:", error);
        } finally {
            btnGerar.disabled = false;
        }
    });
});