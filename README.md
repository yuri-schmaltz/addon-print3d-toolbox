# 3D Print Toolbox (Blender Add-on)

Conjunto de utilidades para preparar modelos para impressão 3D diretamente no Blender. O add-on adiciona um painel lateral **3D Print** no modo *Object* ou *Edit Mesh*, reunindo ferramentas de análise, limpeza, edição e exportação.

## Instalação
1. No Blender, acesse **Edit → Preferences → Add-ons**.
2. Clique em **Install...** e selecione o arquivo compactado do add-on.
3. Ative **3D Print Toolbox**. O painel aparecerá na aba **3D Print** da região **UI** do *Viewport*.

## Fluxo de uso
O painel organiza as ações em quatro seções:

### Analyze
- **Volume / Area**: calcula métricas da malha ativa, respeitando a escala/unidade da cena.
- **Checks**: executa verificações comuns de preparação para impressão:
  - **Solid**: detecta malha aberta ou com buracos.
  - **Intersect**: identifica faces auto-intersectantes.
  - **Degenerate**: encontra geometrias inválidas; o limite é configurado em `Limit` (Scene → Print 3D → Limit).
  - **Non-Flat Faces**: sinaliza faces com ângulo acima de `Angle` (configurável).
  - **Thickness**: mede espessura mínima usando `Minimum Thickness`.
  - **Sharp Edge**: destaca arestas acima de `Angle`.
  - **Overhang**: marca superfícies com inclinação maior que `Angle`.
- **Check All**: executa todas as verificações em sequência.
- Os resultados ficam em **Result**; no modo *Edit* é possível selecionar diretamente os elementos reportados.

### Clean Up
- **Make Manifold**: tenta corrigir não-manifolds (operações internas do Blender).

### Edit
- **Hollow**: cria superfície deslocada (interna ou externa) usando VDB. Exige NumPy e `openvdb` (ou `pyopenvdb` em versões anteriores ao Blender 4.4).
- **Align XY**: alinha o objeto ao plano XY.
- **Scale To**: ajusta a malha pelo **Volume** ou **Bounds** alvo.

### Export
- Define **Export Directory** e **Format** (OBJ, PLY ou STL).
- Opções gerais: `ASCII`, `Scene Scale` e **Copy Textures**.
- Opções de geometria (exceto STL): `UVs`, `Normals` e `Colors`.
- Clique em **Export** para gerar o arquivo com as configurações aplicadas.

## Preferências e propriedades
As configurações ficam em `Scene → Print 3D` e são usadas pelas operações de análise e exportação. As mensagens de resultado podem ser acessadas via `Scene.print3d_toolbox.get_report()` para integrações.

## Localização
O add-on inclui traduções (`localization/*.po`) para múltiplos idiomas. O Blender seleciona automaticamente o idioma ativo e registra as cadeias ao registrar o add-on.

## Suporte e licença
- Compatível com **Blender 4.2+** (veja `blender_manifest.toml`).
- Licença **GPL-3.0-or-later**; autores listados no manifesto e cabeçalhos de arquivo.
- Repositório oficial: [projects.blender.org/extensions/print3d_toolbox](https://projects.blender.org/extensions/print3d_toolbox).
