Peças 3D x Desenhos 2D - Comparador de Imagens
Este projeto visa criar uma ferramenta para comparar imagens de peças 3D com desenhos 2D. O sistema analisa fotos de peças, compara com desenhos armazenados localmente (em C: ou servidor) e, com base em um banco de dados, identifica automaticamente a peça correspondente.

Funcionalidades
Análise de Fotos de Peças: O sistema permite tirar fotos (prints) de peças e comparar com desenhos 2D armazenados.
Armazenamento de Imagens: Armazena uma memória de todas as peças, permitindo que, na próxima vez que um print for feito, o sistema busque o desenho 2D correspondente.
Comparação Automática: Ao tirar um novo print de uma peça, o sistema verifica se a peça já foi identificada no banco de dados, e se sim, exibe a imagem correspondente do desenho 2D.
Localização de Arquivos: O usuário define onde as imagens serão buscadas no diretório local (C: ou servidor).
Instalação
Clone o repositório:

bash
Copiar
Editar
git clone https://github.com/seuusuario/peças-3d-comparador.git
Instale as dependências:

Use o gerenciador de pacotes pip para instalar as bibliotecas necessárias:

bash
Copiar
Editar
pip install opencv-python numpy Pillow scikit-image
Configuração do Diretório de Imagens:

No arquivo config.py, defina o caminho onde as imagens das peças e desenhos 2D serão armazenadas. O caminho pode ser local (C:) ou um servidor compartilhado:

python
Copiar
Editar
image_directory = 'C:/caminho/para/as/imagens/'
Como Usar
Adicionar Peças ao Banco de Dados:

Coloque as imagens de peças e seus desenhos 2D no diretório especificado. O sistema irá salvar esses dados para futuras comparações.

Tirar Print da Peça:

Tire uma foto da peça usando o sistema e o arquivo será automaticamente comparado com os desenhos 2D armazenados.

Verificar Resultados:

O sistema exibirá a imagem do desenho 2D correspondente à peça identificada. Se a peça não for encontrada, ele notificará que a peça não foi identificada.

Contribuições
Se você tiver ideias para melhorar o sistema, fique à vontade para fazer um fork deste repositório e enviar pull requests. Certifique-se de seguir as boas práticas de codificação e incluir testes para qualquer nova funcionalidade.

Licença
Este projeto está licenciado sob a MIT License.
