# Linux Paint

Um editor de imagens com a familiaridade do Paint clássico, uma ribbon compacta e visual pensado para o desktop Linux. Desenvolvido em Python e Qt/PySide6, com distribuição e suporte voltados ao Linux x86_64.

![Linux Paint no GNOME em modo escuro](screenshots/linux-paint-native-wayland.png)

## Baixar

Os pacotes prontos estão em [Releases](https://github.com/DjaboDev/Linux-Paint/releases/latest):

| Formato | Uso |
|---|---|
| `.tar.gz` | Executável independente com instalador local, sem sudo |
| `.AppImage` | Arquivo portátil, com as dependências incluídas |
| `.flatpak` | Aplicativo isolado, integrado ao desktop pelo Flatpak |
| `.deb` | Instalação em Debian, Ubuntu e derivados |
| `.rpm` | Instalação em Fedora e distribuições compatíveis com RPM |

Os cinco formatos são gerados a partir do mesmo código e executável Linux. Cada pacote passa por verificação de estrutura e teste de inicialização; arquivos `.sha256` acompanham os downloads. A linha de releases foi reiniciada na **0.4.0**, reunindo as melhorias das versões anteriores. Windows e macOS não recebem pacotes nem suporte nesta fase.

### Instalar

No AppImage, permita a execução e abra o arquivo:

```bash
chmod +x LinuxPaint-0.4.0-linux-x86_64.AppImage
./LinuxPaint-0.4.0-linux-x86_64.AppImage
```

Se FUSE não estiver disponível, adicione `--appimage-extract-and-run`.

No `.tar.gz`, extraia e abra `LinuxPaint/LinuxPaint`. Para adicionar ao menu de aplicativos, execute `./install.sh` dentro da pasta extraída. O instalador não precisa de sudo.

No Debian/Ubuntu, use `sudo apt install ./LinuxPaint-0.4.0-linux-x86_64.deb`. No Fedora, use `sudo dnf install ./LinuxPaint-0.4.0-linux-x86_64.rpm`.

Para o Flatpak, habilite o Flathub para obter o runtime e instale o arquivo baixado:

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./LinuxPaint-0.4.0-linux-x86_64.flatpak
flatpak run io.github.DjaboDev.LinuxPaint
```

O bundle Flatpak é distribuído por este repositório; isso não significa que o aplicativo foi publicado no catálogo Flathub. O runtime Freedesktop 25.08 é obtido separadamente. O aplicativo tem acesso à pasta pessoal para abrir/salvar imagens e à rede para baixar o modelo opcional de IA; o recorte é processado localmente. O Flatpak mantém configurações e cache em sua pasta isolada.

A instalação por pacote usa `/opt/linux-paint`; o instalador do tar.gz usa `~/.local/share/LinuxPaint-binary`. Evite manter os dois lançadores instalados ao mesmo tempo. O ícone da janela e do lançador usam a mesma identidade no GNOME/Wayland e no X11.

## Ferramentas

- Barra superior unificada com arquivo, salvar, desfazer/refazer e controles da janela.
- Tema escuro por padrão; opção de tema claro, com ribbon, menus e diálogos acompanhando a troca.
- Ribbon com seleção, recorte, redimensionamento, rotação, lápis, pincéis, borracha, texto, formas e cores.
- Pincéis redondo, quadrado e aerógrafo, com ícones que acompanham o tipo selecionado.
- Espessura de 1 a 200 px no lápis, pincéis, borracha e formas; atalhos `[` / `]` e dureza da borda nas ferramentas de desenho. Formato da borracha nas opções da ferramenta.
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
source .venv/bin/activate
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

`build.py` gera o executável Linux, o tar.gz e o AppImage e executa `--self-test`, incluindo Qt, o ícone, OpenCV e ONNX Runtime. `linux_packages.py` gera e testa deb, rpm e Flatpak. O workflow usa Ubuntu 22.04 x86_64, instala as ferramentas de empacotamento e o runtime/SDK Flatpak e publica os cinco formatos juntos após as verificações.

## Organização

| Arquivo | Responsabilidade |
|---|---|
| `classic_paint/app.py` | Editor, canvas, histórico e eventos |
| `classic_paint/modern_ui.py` | Ribbon simbólica, tema e identidade do aplicativo |
| `classic_paint/cutout.py` | Máscaras, seleção por cor, GrabCut e inferência IA |
| `classic_paint/cutout_dialog.py` | Prévia e ferramentas de correção do recorte |
| `build.py` / `linux_packages.py` | Executável Linux, cinco formatos, testes empacotados e hashes |
| `install_linux.py` / `linux/install-packaged.sh` | Integração por código / por pacote no Linux |

## Créditos e licença

Desenvolvimento do fork: [DjaboDev/Linux-Paint](https://github.com/DjaboDev/Linux-Paint). Base original: [blankresearch/ClassicPaint](https://github.com/blankresearch/ClassicPaint).

Código do projeto sob licença MIT. O ícone e a ribbon atuais foram criados para Linux Paint. Recursos legados herdados do projeto original podem ter licença própria; veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Este projeto é independente da Microsoft.

A remoção inteligente utiliza [OpenCV/GrabCut](https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html), [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) e [ONNX Runtime](https://onnxruntime.ai/). A origem do modelo e sua configuração são documentadas nos avisos de terceiros.
