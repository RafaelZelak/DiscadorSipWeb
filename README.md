# DiscadorSipWeb

## Status do Projeto

O projeto **DiscadorSipWeb** foi descontinuado devido a problemas técnicos relacionados à biblioteca PJSUA2 Python. A biblioteca, projetada para aplicações desktop, apresentou dificuldades ao ser adaptada para um ambiente web com Flask e servidores Linux, especificamente no reconhecimento do dispositivo de áudio padrão.

## Motivo da Descontinuação

Ao migrar o projeto para um ambiente web, a biblioteca PJSUA2 Python enfrentou problemas com a compatibilidade de áudio. A biblioteca foi desenvolvida para aplicações desktop, e não foi possível adaptar suas funcionalidades para funcionar corretamente em um ambiente web, levando a problemas com o reconhecimento do dispositivo de áudio padrão.

## Projeto Continuado

O desenvolvimento foi continuado no novo repositório [WebphoneJavaScriptAPI](https://github.com/RafaelZelak/WebphoneJavaScriptAPI). Neste novo projeto, a arquitetura foi modificada para utilizar uma API JavaScript para a operação do webphone via WebSocket, ainda com o Flask no backend. Esta abordagem resolve as limitações encontradas com a biblioteca PJSUA2 e oferece uma solução mais robusta e adequada para aplicações web.

## Repositório Continuado

- [WebphoneJavaScriptAPI](https://github.com/RafaelZelak/WebphoneJavaScriptAPI)
