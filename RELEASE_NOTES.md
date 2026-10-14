# Linux Paint 0.4.0 — nova base Linux

- O lápis respeita a espessura escolhida, de 1 a 200 px, e não herda o formato do pincel anterior.
- A dureza da borda funciona no lápis, nas linhas e em todas as formas geométricas, incluindo as preenchidas. A suavização afeta apenas a nova forma e preserva o desenho existente.
- Desenhar formas com o botão direito troca corretamente as cores do contorno e do preenchimento.
- Os atalhos [ e ] ajustam a espessura e mantêm os controles da ribbon sincronizados; Ctrl + e Ctrl - continuam controlando o zoom.
- O cursor do lápis acompanha o tamanho selecionado.

Esta 0.4.0 reinicia a numeração e reúne todas as melhorias anteriores: ícone próprio, barra superior unificada, ribbon compacta, temas claro/escuro corrigidos, seletor nativo de arquivos, remoção local de fundo por IA/seleção mágica/GrabCut, controles legíveis e prévia de resize.

Distribuição exclusivamente Linux x86_64 em tar.gz, AppImage, Flatpak, deb e rpm. Windows e macOS deixam de ser distribuídos nesta fase. Testes de regressão cobrem espessura, dureza em todas as formas, cores, limites da tela e desfazer/refazer. Os pacotes passam por teste de inicialização e acompanham SHA256.
