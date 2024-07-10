let callerValue = "";
const tempoTotal = 7000;
let callButton = document.getElementById('callButton');
let timerElement = document.getElementById('timer');
let timer;
let seconds = 0;

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('novo_ramal').addEventListener('click', function() {
        document.querySelector('.show_screen').classList.add('hide');
        document.querySelector('.config_screen').classList.remove('hide');
    });

    document.getElementById('cancelar').addEventListener('click', function() {
        document.querySelector('.config_screen').classList.add('hide');
        document.querySelector('.show_screen').classList.remove('hide');
    });

    document.getElementById('salvar').addEventListener('click', function() {
        document.querySelector('.config_screen').classList.add('hide');
        document.querySelector('.show_screen').classList.remove('hide');
    });
});


document.addEventListener('DOMContentLoaded', function() {
    var inputNome = document.getElementById('nome');

    inputNome.addEventListener('input', function() {
        var valor = inputNome.value;
        
        valor = valor.replace(/[^\w\s]/gi, '');
        
        if (valor.length > 25) {
            valor = valor.slice(0, 25);
            inputNome.classList.add('error');
            
            setTimeout(function() {
                inputNome.classList.remove('error');
            }, 1000);
        }  
        inputNome.value = valor;
    });
});


document.addEventListener('DOMContentLoaded', function() {

    fetch('/trigger-sip')
        .then(response => response.text())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Erro ao enviar sinal para Flask:', error);
        });
});

callButton.addEventListener('click', function() {
    if (callButton.innerText === 'Atender') {
        startTimer();
    } else{}
});

function startTimer() {
    timer_start = true;
    if (timer_start) {
        timerElement.innerText = '00:00:00';
        timer = setInterval(updateTime, 1000);
    }
}

function stopTimer() {
    clearInterval(timer);
    seconds = 0;
    timerElement.innerText = 'Digite um número';
}

function updateTime() {
    seconds++;
    timerElement.innerText = formatTime(seconds);
}

function formatTime(seconds) {
    let hrs = Math.floor(seconds / 3600);
    let mins = Math.floor((seconds % 3600) / 60);
    let secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function limparCache() {
    if (window.location.href.indexOf('?timestamp=') === -1) {
        var novaURL = window.location.href + '?timestamp=' + new Date().getTime();
        
        window.location.replace(novaURL);
    }
}

document.getElementById('phoneNumber').addEventListener('input', function() {
  let formattedValue = formatPhoneNumber(this.value);
  this.value = formattedValue;
  
  let numberType = checkNumberType(this.value);
  document.querySelector('.formatNumber').textContent = numberType;
});

// Função para formatar o número de telefone
function formatPhoneNumber(number) {
  let cleaned = number.replace(/[^\d]/g, '');
  
  if (cleaned.length <= 4) {
      return cleaned;
  } else if (cleaned.length <= 6) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`;
  } else if (cleaned.length <= 10) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 6)}-${cleaned.slice(6)}`;
  } else {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`;
  }
}

// Função para verificar o tipo de número (ramal, fixo, celular ou sem formato)
function checkNumberType(number) {
  let cleaned = number.replace(/[^\d]/g, '');
  
  if (cleaned.length < 3) {
      return 'Sem formato';
  }else if (cleaned.length == 4){
      return 'Ramal';
  }else if (cleaned.length === 10 || cleaned.length === 11) {
      let thirdDigit = cleaned[2];
      if (thirdDigit === '9') {
          return 'Celular';
      } else {
          return 'Fixo';
      }
  } else {
      return 'Sem formato';
  }
}

// Função para adicionar um número ao campo phoneNumber
function addNumber(number) {
  let phoneNumber = document.getElementById('phoneNumber');
  let currentValue = phoneNumber.value.replace(/[^\d]/g, '');
  
  if (currentValue.length < 11) {
      let newValue = currentValue + number;
      phoneNumber.value = formatPhoneNumber(newValue);
      
      // Atualizar o tipo de número ao adicionar um dígito
      let numberType = checkNumberType(phoneNumber.value);
      document.querySelector('.formatNumber').textContent = numberType;
  }
}

function sanitizeInput() {
    const inputElement = document.getElementById('phoneNumber');
    const validCharacters = /[0-9\(\)\-]/g;

    // Remove caracteres inválidos
    inputElement.value = inputElement.value.match(validCharacters)?.join('') || '';
}


document.getElementById("callButton").addEventListener("click", function() {
  var phoneNumber = document.getElementById("phoneNumber").value;
  fetch('/make_call', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ phone_number: phoneNumber })
  })


  .then(response => response.json())
  .then(data => {
      if (data.success) {
          console.log(data.success);
      } else if (data.error) {
          console.error(data.error);
      }
  })
  .catch(error => {
      console.error('Error:', error);
  });
});


if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js')
      .then(function() {
          console.log('Service Worker Registered');
      })
      .catch(function(error) {
          console.error('Service Worker registration failed:', error);
      });
}

window.addEventListener('load', function() {
    var phoneNumberInput = document.getElementById('phoneNumber');
    phoneNumberInput.focus();
  
    document.addEventListener('keydown', function(event) {
        if ((event.key >= '0' && event.key <= '9') || event.key === 'Backspace') {
            phoneNumberInput.focus();
        }
    });
  });

document.getElementById("callButtonRecusar").addEventListener("click", function() {
    fetch('/recuse_call', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ phone_number: phoneNumber })
    })
    .then(response => response.json())
    .then(data => {
        if (data.result === true) {
            console.log("Chamada recusada com sucesso!");
        } else {
            console.log("Falha ao recusar chamada.");
        }
    })
    .catch(error => {
        console.error("Erro:", error);
    });
});

async function verificarEstadoConexao() {
    let recebendo = await recebendoLigacao();
    if (recebendo) {
        var phoneNumberInput = document.getElementById('phoneNumber');
        phoneNumberInput.value = callerValue;
        phoneNumberInput.disabled = true;
        document.getElementById('callButton').innerText = 'Atender';
        document.getElementById('callButtonRecusar').innerText = 'Recusar';

        callButtonRecusar.classList.remove('call-button-ligacao-recusar-hide');
        callButtonRecusar.classList.add('call-button-ligacao-recusar');

        callButton.classList.remove('call-button-disconnected', 'call-button-connected', 'call-button-ligacao-atender');
        callButton.classList.add('call-button-ligacao-atender');

        setTimeout(async function() {
            recebendo = false;

            try {
                const response = await fetch('/recebendo_true', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ recebendo: true })
                });
                if (!response.ok) {
                    throw new Error('Erro ao enviar sinal para Flask');
                }
            } catch (error) {
                console.error('Erro ao enviar sinal para Flask:', error);
            }
        }, 7000);

    } else {
        try {
            const response = await fetch('/estado_conexao');
            if (!response.ok) {
                throw new Error('Erro ao obter o estado de conexão');
            }
            const data = await response.json();
            if (data.conectado) {
                var phoneNumberInput = document.getElementById('phoneNumber');
                phoneNumberInput.disabled = false;

                callButtonRecusar.classList.remove('call-button-ligacao-recusar');
                callButtonRecusar.classList.add('call-button-ligacao-recusar-hide');

                document.getElementById('callButton').innerText = 'Desligar';

                callButton.classList.remove('call-button-disconnected', 'call-button-ligacao-atender');
                callButton.classList.add('call-button-connected');

            } else {
                var phoneNumberInput = document.getElementById('phoneNumber');
                phoneNumberInput.disabled = false;

                document.getElementById('callButton').innerText = 'Ligar';
                stopTimer();
                callButtonRecusar.classList.remove('call-button-ligacao-recusar');
                callButtonRecusar.classList.add('call-button-ligacao-recusar-hide');

                callButton.classList.remove('call-button-connected', 'call-button-ligacao-atender');
                callButton.classList.add('call-button-disconnected');
                sanitizeInput();
            }
        } catch (error) {
            console.error('Erro ao verificar o estado de conexão:', error);
        }
    }
}

async function recebendoLigacao() {
    try {
        const response = await fetch('/recebendo_ligacao');
        const data = await response.json();
        
        if (data.caller && data.caller !== "" && data.caller !== null) {
            console.log('Ligação recebida de:', data.caller);
            callerValue = data.caller;
            return true;
        } else {
            console.log('Nenhuma ligação recebida.');
            return false;
        }
    } catch (error) {
        return false;
    }
}

function iniciarVerificacaoPeriodica() {
    setInterval(verificarEstadoConexao, 500);
}

function iniciarRecebendoLigacao() {
    setInterval(recebendoLigacao, 500);
}

document.addEventListener('DOMContentLoaded', function() {
    iniciarVerificacaoPeriodica();
    iniciarRecebendoLigacao();

});
