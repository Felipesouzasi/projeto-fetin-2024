$(document).ready(function() {
    let maxPessoas = 0;

    $('#startBtn').click(function() {
        maxPessoas = parseInt($('#maxPessoas').val());
        if (isNaN(maxPessoas) || maxPessoas <= 0) {
            alert("Por favor, insira um número válido de pessoas.");
            return;
        }

        // Atualiza a URL do vídeo com o número máximo de pessoas
        $('#video').attr('src', '/video_feed?max_pessoas=' + maxPessoas);

        // Exibe o contêiner do vídeo e esconde o formulário
        $('#video-container').show();
        $('#form-container').hide();

        // Inicia a atualização do contador de pessoas
        updatePeopleCount(maxPessoas);
        setInterval(function() {
            updatePeopleCount(maxPessoas);
        }, 1000);
    });

    function updatePeopleCount(maxPessoas) {
        $.ajax({
            url: '/get_people_count',
            method: 'GET',
            success: function(data) {
                let totalPessoas = data.total_pessoas;
                let cntDown = data.cnt_down;

                // Atualiza a legenda do número de pessoas no local
                if (totalPessoas >= maxPessoas) {
                    $('#totalPessoas').text(totalPessoas).css('color', 'red');
                    $('#status').text('LOTADO!').css('color', 'red');
                } else {
                    $('#totalPessoas').text(totalPessoas).css('color', 'green');
                    $('#status').text('').css('color', 'white');
                }

                // Atualiza a legenda do total de pessoas que já estiveram no local
                $('#cntDown').text(cntDown).css('color', 'white');
            },
            error: function(error) {
                console.log('Erro ao obter a contagem de pessoas:', error);
            }
        });
    }
});
