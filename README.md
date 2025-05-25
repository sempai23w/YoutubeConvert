# YoutubeConvert

YoutubeConvert é uma aplicação de desktop que permite baixar e converter vídeos do YouTube de forma simples e eficiente. Ele possui uma interface gráfica amigável construída com `customtkinter`.

## Funcionalidades

- **Download de vídeos do YouTube**: Insira a URL do vídeo e faça o download diretamente.
- **Conversão de formatos**: Converta vídeos para diferentes formatos de áudio e vídeo.
- **Interface moderna**: Interface gráfica intuitiva e personalizável.
- **Notificações**: Receba notificações sobre o status do download.

## Tecnologias Utilizadas

- **Python**: Linguagem principal do projeto.
- **customtkinter**: Para a interface gráfica.
- **pytube**: Para manipulação e download de vídeos do YouTube.
- **pydub**: Para conversão de arquivos de áudio.
- **yt-dlp**: Para suporte avançado a downloads.

## Requisitos

Certifique-se de ter o Python 3.11 ou superior instalado. As dependências podem ser instaladas com o seguinte comando:

```bash
pip install -r requirements.txt
```

## Como Usar

1. Clone este repositório:
   ```bash
   git clone https://github.com/sempai23w/YoutubeConvert
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```bash
   python main.py
   ```

## Estrutura do Projeto

- `main.py`: Arquivo principal para iniciar o aplicativo.
- `gui.py`: Contém a interface gráfica do usuário.
- `downloader.py`: Lida com o download e conversão de vídeos.
- `requirements.txt`: Lista de dependências do projeto.
- `settings.json`: Configurações do aplicativo.
- `icone.ico`: Ícone do aplicativo.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.