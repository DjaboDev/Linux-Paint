# Linux Paint

Um editor de imagens com a familiaridade do Paint clássico, uma ribbon compacta e visual pensado para o desktop Linux. Desenvolvido em Python e Qt/PySide6, também disponível para Windows e macOS.

![Linux Paint no GNOME em modo escuro](screenshots/linux-paint-native-wayland.png)

## Baixar

Os pacotes prontos estão em [Releases](https://github.com/DjaboDev/Linux-Paint/releases/latest):

| Sistema | Pacote |
|---|---|
| Linux x86_64 | `.AppImage` portátil ou `.tar.gz`, com executável e instalador local |
| Windows x86_64 | `.exe` portátil |
| macOS Intel | `.dmg` x86_64 |
| macOS Apple Silicon | `.dmg` arm64 |

Cada pacote é compilado e passa por um teste de inicialização no próprio sistema de destino. Os arquivos `.sha256` permitem verificar a integridade do download. Os pacotes ainda não têm assinatura comercial nem notarização Apple; no macOS, use **Abrir** pelo menu de contexto quando necessário.

### Linux

Para o AppImage, permita a execução do arquivo e abra-o:

```bash
chmod +x LinuxPaint-*-linux-x86_64.AppImage
./LinuxPaint-0.4.1-linux-x86_64.AppImage
```

Se o sistema não disponibilizar FUSE, use `--appimage-extract-and-run` ao abrir. O AppImage contém o aplicativo e suas dependências; o modelo IA continua no cache local, compartilhado com a versão instalada.

Para o `.tar.gz`, extraia o pacote e execute `LinuxPaint/LinuxPaint`. Para adicionar ao menu de aplicativos:

```bash
cd LinuxPaint
./install.sh
```

O instalador não precisa de `sudo`. O ícone da janela e o lançador usam a mesma identidade no GNOME/Wayland e no X11.

### Windows e macOS

No Windows, abra o `.exe`. No macOS, abra o `.dmg`, arraste **LinuxPaint.app** para **Applications** e abra o aplicativo.

## Ferramentas

- Barra superior unificada com arquivo, salvar, desfazer/refazer e controles da janela.
- Tema escuro por padrão; opção de tema claro, com ribbon, menus e diálogos acompanhando a troca.
- Ribbon com seleção, recorte, redimensionamento, rotação, lápis, pincéis, borracha, texto, formas e cores.
- Pincéis redondo, quadrado e aerógrafo, com ícones que acompanham o tipo selecionado.
- Espessura com exemplos visuais, ajuste numérico e dureza real; formato da borracha nas opções da ferramenta.
- Réguas, grade, zoom, alças de resize com prévia visível e histórico de desfazer/refazer.
- Seletor nativo de arquivos no Linux, com pastas e prévias oferecidas pelo desktop; abertura na pasta pessoal do usuário.
- Abertura e exportação de imagens; transparência real em PNG e aviso antes de achatá-la em JPEG/BMP.

## Remover fundo

![Editor de remoção de fundo](screenshots/remove-background.png)

Abra uma imagem e clique em **Remover fundo**, à direita das cores na ribbon.

1. Use **Detectar pelas bordas** para fundos simples, ou **Seleção mágica** e clique no fundo. A tolerância controla o quanto as cores podem variar; **Área conectada** evita apagar regiões isoladas da mesma cor.
2. Para fotografias e fundos complexos, use **Baixar modelo IA**, depois **Detectar com IA**. O modelo BiRefNet General Lite é baixado uma vez, verificado e armazenado no cache local. As imagens são processadas no computador e não são enviadas a um serviço.
3. Corrija o recorte com **Manter** e **Apagar**. **Refinar com marcações** usa GrabCut para ajustar a separação. Você pode desfazer ajustes e recomeçar.
4. Confira em transparência, branco e fundo escuro. Ajuste suavização, expansão/retração e redução de halo quando necessário. Use a roda para ampliar e o botão do meio para deslocar a prévia.
5. Clique em **Aplicar recorte** e salve em **PNG**. O editor mantém o original até a aplicação, e `Ctrl+Z` desfaz o resultado.

A detecção automática é um ponto de partida: cabelos, transparências, sombras, objetos colados nas bordas e cores semelhantes entre fundo e objeto podem precisar de correções. As marcações manuais têm prioridade sobre a máscara automática. A suavização e o recorte nunca tornam opacos pixels que já eram transparentes.

O processamento ocorre em uma tarefa separada. Cancelar preserva a imagem; uma inferência já iniciada pode levar alguns segundos para terminar. O modelo não acompanha o executável, evitando inflar os downloads; o primeiro uso de IA precisa de internet para baixar cerca de 220 MB. As ferramentas por cor e GrabCut funcionam sem esse download.

## Rodar pelo código

Use Python 3.12 em um ambiente virtual:

```bash
python3.12 -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python paint.py
```

Para instalar a versão por código no Linux, use `python install_linux.py` com o ambiente virtual ativo. Esse caminho usa o interpretador do ambiente: mantenha-o no local original. O instalador mantém o comando legado `classic-paint`, guarda uma cópia do lançador anterior e migra seu favorito no GNOME.

## Testes e compilação

```bash
python -m unittest discover -v
python smoke.py
python check_ui.py
python build.py
```

Os testes verificam desenho, histórico, cores, temas, pincéis, resize, máscaras, transparência, correções manuais, cancelamento e aplicação reversível. `check_ui.py` também renderiza a interface em QHD. A inferência IA é conferida separadamente com o modelo real; os testes normais não baixam pesos pela rede.

`build.py` compila no sistema/arquitetura atual e executa `--self-test` no binário gerado, incluindo Qt, o ícone, OpenCV e ONNX Runtime. O workflow do GitHub produz os pacotes para os quatro destinos e o AppImage Linux e só publica uma release marcada `v*` quando todos os builds passam.

## Organização

| Arquivo | Responsabilidade |
|---|---|
| `classic_paint/app.py` | Editor, canvas, histórico e eventos |
| `classic_paint/modern_ui.py` | Ribbon simbólica, tema e identidade do aplicativo |
| `classic_paint/cutout.py` | Máscaras, seleção por cor, GrabCut e inferência IA |
| `classic_paint/cutout_dialog.py` | Prévia e ferramentas de correção do recorte |
| `build.py` | Executáveis, teste empacotado e hashes |
| `install_linux.py` / `linux/install-packaged.sh` | Integração por código / por pacote no Linux |

## Créditos e licença

Desenvolvimento do fork: [DjaboDev/Linux-Paint](https://github.com/DjaboDev/Linux-Paint). Base original: [blankresearch/ClassicPaint](https://github.com/blankresearch/ClassicPaint).

Código do projeto sob licença MIT. O ícone e a ribbon atuais foram criados para Linux Paint. Recursos legados herdados do projeto original podem ter licença própria; veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Este projeto é independente da Microsoft.

A remoção inteligente utiliza [OpenCV/GrabCut](https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html), [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) e [ONNX Runtime](https://onnxruntime.ai/). A origem do modelo e sua configuração são documentadas nos avisos de terceiros.
