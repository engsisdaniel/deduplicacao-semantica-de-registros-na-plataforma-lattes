"""
Gerador incremental de cache/test.json para testes de deduplicação.

Uso:
    python scripts/generate_test_batch.py --batch <N>   # Gera lote N (1-10)
    python scripts/generate_test_batch.py --merge       # Mescla todos os lotes em cache/test.json
    python scripts/generate_test_batch.py --status      # Mostra quais lotes já foram gerados

Cada lote N cobre as triplas (N-1)*10+1 até N*10.
Ex: lote 1 → triplas 1-10 → ids 1-10, 101-110, 201-210
"""

import json
import os
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "lotes")
MAP_FILE = os.path.join(CACHE_DIR, "test_map.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "base_sintetica.json")


# ---------------------------------------------------------------------------
# DADOS DOS PROJETOS (10 triplas por bloco, 10 blocos)
# ---------------------------------------------------------------------------

PROJECTS_DATA = {
    # ---- BLOCO 1: IDs 1-10 (Educação) ------------------------------------
    1: {
        "titulo": "PIBID: Formação Docente e Iniciação à Docência no Ensino Médio",
        "descricao": (
            "O Programa Institucional de Bolsas de Iniciação à Docência (PIBID) da Universidade Federal do "
            "Paraná tem como objetivo principal promover a inserção dos estudantes de licenciatura no cotidiano "
            "das escolas públicas de educação básica, contribuindo para a articulação entre teoria e prática "
            "necessária à formação dos docentes. O projeto envolve 120 estudantes de cursos de licenciatura "
            "em Matemática, Física, Química, Biologia, História e Letras, distribuídos em 8 escolas estaduais "
            "parceiras do município de Curitiba e região metropolitana. As atividades desenvolvidas incluem "
            "planejamento colaborativo de aulas, regência supervisionada, produção de materiais didáticos e "
            "participação em reuniões pedagógicas. Cada subprojeto conta com a supervisão de um professor da "
            "escola parceira e a coordenação de um docente da universidade. Os resultados esperados incluem "
            "a melhoria dos índices de desempenho dos alunos nas disciplinas atendidas, o fortalecimento da "
            "identidade docente dos bolsistas e a produção de relatos de experiência e artigos científicos "
            "sobre as práticas pedagógicas desenvolvidas. O projeto tem duração de 24 meses e conta com "
            "financiamento da CAPES por meio do Edital PIBID 2020."
        ),
        "lattes_id": "3821047693150284",
        "autores": "Ana Beatriz Lima, Carlos Eduardo Souza, FERNANDA OLIVEIRA ROCHA"
    },
    2: {
        "titulo": "Extensão Universitária e Letramento Digital em Escolas Públicas",
        "descricao": (
            "Este projeto de extensão universitária tem como objetivo promover o letramento digital de "
            "professores e estudantes de escolas públicas municipais por meio de ações formativas e "
            "oficinas práticas. Diante da crescente demanda por habilidades digitais no contexto educacional "
            "contemporâneo, o projeto propõe a formação de multiplicadores que possam replicar conhecimentos "
            "sobre uso pedagógico de tecnologias nas suas respectivas comunidades escolares. As atividades "
            "abrangem desde o uso básico de dispositivos e ferramentas de produtividade até a criação de "
            "conteúdos digitais educativos, uso responsável de redes sociais e noções de segurança digital. "
            "O projeto prevê a realização de 12 oficinas presenciais e 8 encontros remotos, atendendo "
            "aproximadamente 200 participantes ao longo de um semestre. A metodologia baseia-se na "
            "aprendizagem ativa, com uso de metodologias como sala de aula invertida e aprendizagem "
            "baseada em projetos. Os resultados serão avaliados por meio de instrumentos de verificação "
            "de aprendizagem e questionários de impacto aplicados antes e após as formações."
        ),
        "lattes_id": "5047182930461758",
        "autores": "Marcos Antônio Ferreira, Patrícia Nunes Alves, Renata Cristina Borges"
    },
    3: {
        "titulo": "Formação Continuada de Professores para a Educação Inclusiva",
        "descricao": (
            "A inclusão escolar de estudantes com deficiência, transtornos globais do desenvolvimento e "
            "altas habilidades/superdotação é um desafio constante para os sistemas educacionais brasileiros. "
            "O presente projeto visa promover a formação continuada de professores da rede municipal de "
            "ensino de Londrina para o atendimento inclusivo, com ênfase nas estratégias pedagógicas "
            "diferenciadas, adaptações curriculares e uso de tecnologias assistivas. O projeto será "
            "desenvolvido em parceria com o Núcleo de Educação Especial da Secretaria Municipal de Educação "
            "e envolverá 150 professores do ensino fundamental I e II. As ações formativas incluem "
            "seminários, grupos de estudo, oficinas práticas e acompanhamento em sala de aula. "
            "Prevê-se a produção de um guia prático de estratégias inclusivas, a ser disponibilizado "
            "em formato digital para toda a rede municipal. A avaliação do projeto ocorrerá por meio de "
            "observação participante nas escolas, análise de portfólios dos professores participantes e "
            "aplicação de questionários de autoavaliação ao início e ao final da formação."
        ),
        "lattes_id": "7193824056371049",
        "autores": "Juliana Costa Mendes, Roberto Henrique Prado, SILVIA APARECIDA MONTEIRO"
    },
    4: {
        "titulo": "Educação Ambiental Integrada ao Projeto Pedagógico do Ensino Fundamental",
        "descricao": (
            "O presente projeto tem como objetivo integrar a educação ambiental de forma transversal e "
            "interdisciplinar ao projeto pedagógico de escolas de ensino fundamental do município de "
            "Maringá. A proposta parte do reconhecimento de que a questão ambiental deve ser tratada de "
            "maneira contextualizada, conectando os conteúdos escolares aos problemas socioambientais "
            "vivenciados pelas comunidades. As ações previstas envolvem a formação de professores de "
            "diferentes disciplinas para a incorporação da temática ambiental em seus planejamentos, "
            "a criação de hortas escolares, a realização de visitas a áreas naturais preservadas e "
            "a produção de materiais educativos pelos próprios estudantes. O projeto será desenvolvido "
            "em 5 escolas municipais, envolvendo aproximadamente 800 estudantes dos anos finais do "
            "ensino fundamental. Espera-se que ao final do projeto os estudantes demonstrem maior "
            "consciência ambiental, com atitudes mais sustentáveis em seu cotidiano, e que os professores "
            "tenham ampliado sua capacidade de trabalhar a educação ambiental de forma integrada."
        ),
        "lattes_id": "2847503916482037",
        "autores": "Diego Luiz Carvalho, Elaine Moreira Santos, Tânia Regina Vieira"
    },
    5: {
        "titulo": "Metodologias Ativas e Aprendizagem Cooperativa no Ensino Superior",
        "descricao": (
            "O projeto investiga os impactos da adoção de metodologias ativas de aprendizagem, com ênfase "
            "na aprendizagem cooperativa e na aprendizagem baseada em problemas, no desempenho e na "
            "motivação de estudantes de cursos de graduação em engenharia e ciências exatas. "
            "A pesquisa será conduzida em turmas dos cursos de Engenharia Civil, Engenharia Elétrica e "
            "Bacharelado em Matemática da Universidade Estadual de Maringá, envolvendo aproximadamente "
            "360 estudantes ao longo de dois semestres letivos. O delineamento metodológico prevê "
            "a comparação entre turmas que utilizam metodologias ativas e turmas com ensino convencional "
            "expositivo. Serão aplicados instrumentos de coleta de dados antes e após as intervenções, "
            "incluindo testes de desempenho, escalas de motivação e questionários de percepção dos "
            "estudantes sobre as metodologias empregadas. Os resultados deverão subsidiar propostas de "
            "reformulação curricular nos cursos envolvidos e servir de base para formações docentes "
            "voltadas à inovação pedagógica no ensino superior."
        ),
        "lattes_id": "6310295847163920",
        "autores": "Fábio Augusto Martins, Lúcia Helena Rodrigues, Wagner Correia Neto"
    },
    6: {
        "titulo": "Gamificação no Ensino de Ciências: Avaliação de Aprendizagem e Engajamento",
        "descricao": (
            "A gamificação tem sido apontada como uma estratégia promissora para aumentar o engajamento "
            "e a motivação dos estudantes no processo de ensino-aprendizagem. O presente projeto tem como "
            "objetivo avaliar o impacto de estratégias gamificadas no ensino de Ciências Naturais em "
            "turmas do sexto ao nono ano do ensino fundamental. A pesquisa será realizada em 4 escolas "
            "estaduais do interior do Paraná, envolvendo 320 estudantes e 12 professores. As intervenções "
            "incluem a criação e aplicação de jogos digitais e analógicos baseados nos conteúdos "
            "curriculares de Ciências, bem como a utilização de plataformas de quiz online com elementos "
            "de competição e recompensa. A coleta de dados ocorrerá por meio de pré e pós-testes de "
            "conteúdo, registros de observação em sala de aula e entrevistas com professores e estudantes. "
            "Os dados serão analisados quantitativamente, por meio de testes estatísticos, e qualitativamente, "
            "por análise de conteúdo. Os resultados contribuirão para a produção de um repositório de "
            "jogos educativos de acesso livre para professores de Ciências."
        ),
        "lattes_id": "9182736405192847",
        "autores": "Adriana Gonçalves Leal, Bruno Cesar Teixeira, Mônica Aparecida Figueiredo"
    },
    7: {
        "titulo": "Pedagogia Popular Freiriana em Espaços Educativos Comunitários",
        "descricao": (
            "Fundamentado nos princípios da educação popular desenvolvidos por Paulo Freire, este projeto "
            "propõe ações educativas emancipadoras em comunidades periféricas de Campinas, buscando "
            "articular o saber popular ao conhecimento sistematizado. O projeto atua em 3 centros "
            "comunitários e 2 associações de moradores, desenvolvendo atividades de alfabetização de "
            "adultos, círculos de cultura, oficinas de leitura crítica de mundo e formação de lideranças "
            "locais. A metodologia freiriana pressupõe o diálogo como princípio pedagógico fundamental, "
            "respeitando os saberes dos educandos e partindo da realidade concreta das comunidades para "
            "a construção coletiva do conhecimento. O projeto envolve estudantes de graduação dos cursos "
            "de Pedagogia, Serviço Social e Letras, que atuam como educadores e pesquisadores. "
            "Espera-se contribuir para o fortalecimento da consciência crítica e da cidadania ativa "
            "dos participantes, além de produzir conhecimento sobre as práticas pedagógicas populares "
            "e seu potencial transformador nos contextos comunitários."
        ),
        "lattes_id": "4056738291847362",
        "autores": "Cláudia Regina Pinheiro, EDSON MARCOS ALBUQUERQUE, Vera Lúcia Nascimento"
    },
    8: {
        "titulo": "Avaliação Institucional e Qualidade no Ensino Superior: Uma Análise do SINAES",
        "descricao": (
            "O Sistema Nacional de Avaliação da Educação Superior (SINAES) constitui o principal "
            "mecanismo de avaliação das instituições de ensino superior no Brasil. Este projeto analisa "
            "os processos avaliativos implementados por duas universidades federais e três centros "
            "universitários privados, investigando de que forma os resultados das avaliações externas "
            "são internalizados e utilizados para a melhoria institucional. A pesquisa adota uma "
            "abordagem qualitativa, com realização de entrevistas com gestores acadêmicos, análise "
            "documental de relatórios de autoavaliação e observação de reuniões de planejamento "
            "estratégico. Busca-se compreender os sentidos atribuídos à avaliação pelos atores "
            "institucionais e os fatores que facilitam ou dificultam o uso dos resultados para "
            "aprimorar a qualidade educacional. Os achados da pesquisa deverão contribuir para "
            "o debate sobre as políticas de avaliação da educação superior e para o aperfeiçoamento "
            "dos processos de autoavaliação institucionais, com produção de artigos científicos "
            "e relatório técnico para as instituições participantes."
        ),
        "lattes_id": "8273946105837264",
        "autores": "Alexandre Moura Ramos, Cristiane Batista Lima, Henrique Souza Medeiros"
    },
    9: {
        "titulo": "Ensino Bilíngue Português-Inglês na Educação Básica: Desafios e Perspectivas",
        "descricao": (
            "A crescente expansão do ensino bilíngue em instituições de educação básica no Brasil "
            "suscita questionamentos sobre a qualidade das propostas implementadas e seus impactos "
            "no desenvolvimento linguístico e cognitivo dos estudantes. Este projeto investiga "
            "as práticas pedagógicas adotadas em 6 escolas bilíngues de diferentes perfis "
            "socioeconômicos do município de São Paulo, buscando identificar modelos eficazes "
            "de ensino integrado de conteúdo e língua (CLIL). A pesquisa envolve observações "
            "de aulas, análise de materiais didáticos, entrevistas com professores e coordenadores "
            "pedagógicos e avaliações de proficiência linguística dos estudantes. Um componente "
            "formativo também integra o projeto, com a oferta de oficinas de desenvolvimento "
            "profissional para professores das escolas participantes. Os resultados esperados "
            "incluem a elaboração de diretrizes pedagógicas para o ensino bilíngue na educação "
            "básica e a produção de materiais didáticos bilíngues contextualizados à realidade "
            "brasileira, disponibilizados em repositório aberto."
        ),
        "lattes_id": "1947382056194738",
        "autores": "Beatriz Falcão Cunha, José Carlos Wanderley, Natália Perini Zanatta"
    },
    10: {
        "titulo": "Evasão Escolar no Ensino Médio: Fatores Socioeconômicos e Estratégias de Intervenção",
        "descricao": (
            "A evasão escolar no ensino médio representa um dos maiores desafios da educação brasileira, "
            "com impactos diretos sobre as perspectivas de desenvolvimento social e econômico do país. "
            "Este projeto investiga os principais fatores associados à evasão em escolas estaduais "
            "de municípios com baixo IDH do interior do Ceará, com o objetivo de subsidiar a "
            "formulação de estratégias de intervenção pedagógica e social eficazes. A pesquisa adota "
            "metodologia mista, combinando análise quantitativa de dados do Censo Escolar com "
            "entrevistas em profundidade realizadas com estudantes evadidos, familiares, professores "
            "e gestores escolares. Os resultados preliminares indicam que a necessidade de trabalhar "
            "para complementar a renda familiar, a distância da escola e a percepção de irrelevância "
            "dos conteúdos para a vida cotidiana figuram entre os principais fatores de evasão. "
            "Com base nos resultados, o projeto propõe um modelo de monitoramento e intervenção "
            "precoce para escolas em situação de risco, incluindo sistema de alertas, ações de "
            "reforço escolar e articulação com serviços de assistência social."
        ),
        "lattes_id": "5830197462038471",
        "autores": "Gustavo Henrique Maciel, Isabel Cristina Duarte, Leandro Fonseca Braga"
    },

    # ---- BLOCO 2: IDs 11-20 (Biologia) ------------------------------------
    11: {
        "titulo": "Levantamento Florístico da Mata Atlântica em Fragmentos do Litoral Norte do ES",
        "descricao": (
            "A Mata Atlântica é considerada um dos biomas mais ameaçados do planeta, com menos de 12% "
            "de sua cobertura original preservada. Este projeto tem como objetivo realizar o levantamento "
            "florístico de fragmentos remanescentes de Mata Atlântica no litoral norte do Espírito Santo, "
            "contribuindo para o conhecimento da biodiversidade local e subsidiando ações de conservação "
            "e restauração ecológica. A metodologia inclui expedições de coleta botânica mensais em "
            "15 fragmentos florestais, herborização e identificação taxonômica do material coletado, "
            "com depósito de exsicatas no herbário da instituição. Os dados sobre composição florística, "
            "riqueza de espécies e indicadores de diversidade serão analisados e comparados entre os "
            "fragmentos de diferentes tamanhos e graus de isolamento. Espera-se catalogar mais de "
            "500 espécies de plantas vasculares, com identificação de espécies ameaçadas de extinção "
            "e endêmicas. Os resultados serão publicados em revistas científicas da área e disponibilizados "
            "para os órgãos ambientais estaduais e municipais para fins de planejamento e conservação."
        ),
        "lattes_id": "3748201956473829",
        "autores": "André Luis Pereira, Camila Faria Gomes, Rodrigo Matos Cavalcanti"
    },
    12: {
        "titulo": "Macroinvertebrados Bentônicos como Bioindicadores de Qualidade em Rios do Paraná",
        "descricao": (
            "A comunidade de macroinvertebrados bentônicos tem sido amplamente utilizada como ferramenta "
            "de biomonitoramento da qualidade de ecossistemas aquáticos, dada sua sensibilidade a "
            "alterações físicas, químicas e biológicas da água. Este projeto tem como objetivo avaliar "
            "a qualidade ecológica de 12 rios de médio porte na bacia do rio Ivaí, no Paraná, "
            "utilizando índices bióticos baseados na composição e abundância de macroinvertebrados "
            "bentônicos. As coletas serão realizadas em três períodos sazonais distintos, empregando "
            "protocolos padronizados de amostragem. Os dados biológicos serão correlacionados com "
            "variáveis físico-químicas da água e com informações sobre o uso e cobertura do solo "
            "nas respectivas bacias de drenagem. Os resultados permitirão identificar os principais "
            "estressores ambientais que afetam a integridade ecológica dos cursos d'água estudados "
            "e fornecer subsídios para programas de recuperação de matas ciliares e gestão de "
            "bacias hidrográficas na região."
        ),
        "lattes_id": "6192847305618294",
        "autores": "Daniela Couto Rezende, Felipe Augusto Dias, Mariana Lopes Vasconcelos"
    },
    13: {
        "titulo": "Filogenia Molecular e Biogeografia de Aves Neotropicais do Gênero Thraupidae",
        "descricao": (
            "A família Thraupidae representa um dos grupos mais diversos de aves Neotropicais, com "
            "mais de 370 espécies distribuídas por toda a América do Sul e Central. Este projeto "
            "investiga as relações filogenéticas entre espécies selecionadas do grupo, utilizando "
            "marcadores moleculares de DNA mitocondrial e nuclear, com o objetivo de elucidar os "
            "padrões evolutivos e biogeográficos que moldaram a diversificação do grupo. "
            "Serão analisadas amostras teciduais de 45 espécies coletadas em diferentes biomas "
            "brasileiros, incluindo Amazônia, Cerrado, Caatinga e Mata Atlântica. As análises "
            "filogenéticas serão conduzidas por métodos de máxima verossimilhança e inferência "
            "bayesiana, com calibração temporal baseada em registros fósseis. Os resultados "
            "contribuirão para a revisão taxonômica do grupo e para a compreensão dos processos "
            "históricos de especiação em resposta às variações paleoclimáticas do Neotropico."
        ),
        "lattes_id": "8047293615847302",
        "autores": "Eduardo Siqueira Brandão, Luciana Moraes Abreu, Paulo Roberto Esteves"
    },
    14: {
        "titulo": "Fungos Rizosféricos e Biofertilizantes na Agricultura Orgânica Sustentável",
        "descricao": (
            "O aproveitamento da biodiversidade microbiana do solo como bioinsumos agrícolas representa "
            "uma alternativa promissora para a redução da dependência de fertilizantes químicos sintéticos "
            "na agricultura. Este projeto tem como objetivo isolar, caracterizar e selecionar fungos "
            "rizosféricos com potencial para promoção do crescimento de plantas cultivadas, com ênfase "
            "em fungos micorrízicos arbusculares e fungos solubilizadores de fosfato. Os fungos serão "
            "isolados de solos de sistemas de produção orgânica de hortaliças em municípios da Serra "
            "Gaúcha. A caracterização incluirá testes morfológicos, moleculares e funcionais, com "
            "avaliação do potencial de solubilização de fosfato, produção de fitormônios e tolerância "
            "a condições de estresse. Os isolados mais promissores serão avaliados em experimentos de "
            "casa de vegetação e campo, com culturas de alface, tomate e cebola. Os resultados "
            "deverão contribuir para o desenvolvimento de biofertilizantes adaptados às condições "
            "edafoclimáticas do Sul do Brasil."
        ),
        "lattes_id": "2193847562039481",
        "autores": "Aline Cristina Barbosa, Marcelo Tadeu Freitas, Sandra Mara Costa"
    },
    15: {
        "titulo": "Briófitas do Cerrado: Taxonomia, Distribuição e Conservação",
        "descricao": (
            "As briófitas (musgos, hepáticas e antóceros) compõem um grupo vegetal de grande importância "
            "ecológica, atuando como bioindicadores ambientais, retentores de umidade e berçários para "
            "a fauna invertebrada. No Cerrado, a brioflora é ainda pouco conhecida em comparação com "
            "outros grupos vegetais. Este projeto tem como objetivo realizar o levantamento taxonômico "
            "das briófitas em 10 áreas de Cerrado sensu stricto do estado de Goiás, com coletas "
            "sistemáticas em épocas chuvosa e seca. O material coletado será herborizado e identificado "
            "com base em literatura especializada e consulta a especialistas, com depósito de exsicatas "
            "em herbários de referência. Serão elaboradas chaves de identificação ilustradas para os "
            "gêneros encontrados e mapas de distribuição das espécies registradas. A análise da "
            "composição de espécies permitirá avaliar o estado de conservação das áreas estudadas "
            "e identificar espécies prioritárias para ações de proteção."
        ),
        "lattes_id": "7482930164758201",
        "autores": "Cintia Oliveira Machado, Jorge Henrique Barros, Regina Célia Matos"
    },
    16: {
        "titulo": "Comportamento Social e Ecologia de Primatas em Fragmento Amazônico",
        "descricao": (
            "Os primatas neotropicais estão entre os grupos mais ameaçados pela fragmentação florestal "
            "na Amazônia brasileira. Este projeto investiga o comportamento social, o uso do habitat "
            "e a dieta de grupos de macacos-prego (Cebus apella) e guaribas (Alouatta belzebul) em "
            "um fragmento de floresta de 1.200 hectares no sul do Pará, submetido a pressões "
            "antrópicas crescentes. A metodologia inclui censos populacionais, focal animal "
            "e varredura instantânea, com uso de GPS para mapeamento de áreas de vida. "
            "Amostras fecais serão coletadas para análise dietética por meio de identificação "
            "de itens alimentares e caracterização molecular de parasitas gastrintestinais. "
            "Os resultados permitirão avaliar o impacto da fragmentação sobre o comportamento "
            "e a saúde das populações estudadas, contribuindo para a elaboração de planos de "
            "manejo e conservação de primatas na região."
        ),
        "lattes_id": "3917284650193748",
        "autores": "Fernando Luiz Assis, Kátia Regina Cunha, Thiago Augusto Moreira"
    },
    17: {
        "titulo": "Estrutura e Função de Enzimas Celulolíticas de Fungos Termofílicos",
        "descricao": (
            "A produção de biocombustíveis de segunda geração a partir de biomassa lignocelulósica "
            "requer a atuação de enzimas eficientes na degradação da celulose em condições de "
            "temperatura elevada. Este projeto tem como objetivo isolar, purificar e caracterizar "
            "bioquímica e estruturalmente celulases produzidas por fungos termofílicos isolados "
            "de solos de compostagenm industrial. A triagem dos fungos será realizada em meio "
            "seletivo com celulose como única fonte de carbono a 50°C. As enzimas selecionadas "
            "serão purificadas por cromatografia de troca iônica e gel filtração, e caracterizadas "
            "quanto a temperatura e pH ótimos, termoestabilidade e cinética enzimática. "
            "A determinação da estrutura tridimensional por cristalografia de raios-X ou "
            "modelagem computacional permitirá identificar os resíduos catalíticos e as "
            "características estruturais responsáveis pela termoestabilidade, fornecendo "
            "subsídios para engenharia de enzimas com melhor desempenho industrial."
        ),
        "lattes_id": "5038471920364857",
        "autores": "Giovanna Pereira Ribeiro, Humberto Carlos Neves, Lívia Fernanda Campos"
    },
    18: {
        "titulo": "Respostas Fisiológicas de Plantas do Semiárido ao Estresse Hídrico",
        "descricao": (
            "A vegetação da Caatinga desenvolveu mecanismos fisiológicos sofisticados para sobreviver "
            "às condições extremas de deficiência hídrica características do semiárido nordestino. "
            "Este projeto investiga as respostas fisiológicas e bioquímicas de espécies nativas da "
            "Caatinga, incluindo jurema-preta (Mimosa tenuiflora), umburana (Commiphora leptophloeos) "
            "e catingueira (Poincianella pyramidalis), a diferentes regimes de estresse hídrico "
            "em condições controladas. Serão avaliados parâmetros relacionados ao balanço hídrico "
            "das plantas, trocas gasosas, fluorescência da clorofila, conteúdo de solutos orgânicos "
            "compatíveis e atividade de enzimas antioxidantes. Os resultados contribuirão para "
            "a compreensão dos mecanismos de tolerância à seca nessas espécies e para a seleção "
            "de genótipos mais tolerantes para uso em programas de recuperação de áreas degradadas "
            "no semiárido."
        ),
        "lattes_id": "8201934756081924",
        "autores": "Janaína Sousa Carvalho, Márcio Araújo Lima, Viviane Torres Brito"
    },
    19: {
        "titulo": "Branqueamento de Corais no Recife de Abrolhos: Monitoramento e Conservação",
        "descricao": (
            "Os recifes de coral do Banco dos Abrolhos, no sul da Bahia, abrigam a maior biodiversidade "
            "marinha do Atlântico Sul. O fenômeno de branqueamento, desencadeado pelo aumento da "
            "temperatura da água superficial associado às mudanças climáticas, tem causado mortalidade "
            "crescente de corais em todo o mundo. Este projeto estabelece um programa de monitoramento "
            "de longo prazo das colônias de coral em 8 sítios de amostragem no Banco dos Abrolhos, "
            "documentando eventos de branqueamento, taxa de mortalidade e recuperação. A metodologia "
            "inclui mergulho autônomo com registro fotográfico e videográfico, coleta de fragmentos "
            "teciduais para análises moleculares e medição contínua de temperatura da água por meio "
            "de sensores fixos. Os dados serão integrados a registros de temperatura da superfície "
            "do mar obtidos por sensoriamento remoto. Os resultados subsidiarão propostas de gestão "
            "adaptativa para a Área de Proteção Ambiental Marinha do Recife de Corais."
        ),
        "lattes_id": "1746382059147263",
        "autores": "Kátia Melo Guimarães, Newton Rodrigues Barros, Priscila Sampaio Castro"
    },
    20: {
        "titulo": "Epidemiologia e Controle da Leishmaniose Tegumentar na Região Norte do Brasil",
        "descricao": (
            "A leishmaniose tegumentar americana (LTA) é uma doença negligenciada que afeta populações "
            "rurais e de fronteira agrícola na região Norte do Brasil. Este projeto investiga a "
            "epidemiologia molecular da LTA em 4 municípios do estado do Amazonas, caracterizando "
            "as espécies de Leishmania circulantes, os vetores flebotomíneos envolvidos na transmissão "
            "e os fatores ambientais e socioeconômicos associados ao risco de infecção. "
            "A metodologia inclui inquérito soroepidemiológico em humanos, captura e identificação "
            "de flebotomíneos por armadilhas luminosas, e isolamento e caracterização molecular "
            "dos parasitas de humanos, reservatórios animais e vetores. Os dados serão integrados "
            "em um sistema de informação geográfica para análise espacial da distribuição da "
            "doença. Os resultados deverão subsidiar ações de controle vetorial e orientar "
            "campanhas de educação em saúde nas comunidades mais vulneráveis."
        ),
        "lattes_id": "4920374816592047",
        "autores": "Laís Andrade Ferreira, Otávio Henrique Ramos, Simone Cristina Duarte"
    },

    # ---- BLOCO 3: IDs 21-30 (Computação) ----------------------------------
    21: {
        "titulo": "Aprendizado de Máquina para Classificação de Dados em Saúde Digital",
        "descricao": (
            "A aplicação de técnicas de aprendizado de máquina em dados clínicos tem demonstrado "
            "grande potencial para apoiar o diagnóstico e o prognóstico de doenças. Este projeto "
            "propõe o desenvolvimento e a avaliação de modelos de classificação para predição de "
            "risco cardiovascular em pacientes do Sistema Único de Saúde, utilizando dados "
            "provenientes de prontuários eletrônicos anonimizados de três hospitais públicos. "
            "Serão treinados e comparados algoritmos de Random Forest, Gradient Boosting, "
            "Redes Neurais Artificiais e Support Vector Machines, com ênfase na interpretabilidade "
            "dos modelos por meio de técnicas de explainable AI (XAI). O projeto adota rigorosas "
            "práticas de governança de dados, garantindo anonimização e privacidade. "
            "O desempenho dos modelos será avaliado por métricas como AUC-ROC, sensibilidade, "
            "especificidade e valor preditivo positivo. Os modelos desenvolvidos serão integrados "
            "a um protótipo de sistema de suporte à decisão clínica para validação em ambiente real."
        ),
        "lattes_id": "7384920165738402",
        "autores": "Arthur Rocha Mendonça, Débora Lima Furtado, Igor Vasconcelos Braga"
    },
    22: {
        "titulo": "Computação em Nuvem: Latência e Desempenho em Sistemas Distribuídos",
        "descricao": (
            "A migração de aplicações críticas para ambientes de computação em nuvem apresenta "
            "desafios relacionados à latência, disponibilidade e consistência dos dados. "
            "Este projeto investiga técnicas de otimização de desempenho em sistemas distribuídos "
            "implantados em infraestruturas de nuvem híbrida, com foco na redução de latência "
            "em aplicações de tempo real. A pesquisa propõe um framework de monitoramento e "
            "escalonamento automático baseado em métricas de qualidade de serviço, utilizando "
            "algoritmos de aprendizado por reforço para tomada de decisão adaptativa. "
            "Os experimentos serão conduzidos em ambientes de nuvem pública (AWS e Azure) "
            "e privada (OpenStack), com diferentes cargas de trabalho sintéticas e reais. "
            "O framework desenvolvido será comparado com soluções comerciais existentes, "
            "avaliando ganhos em termos de latência, throughput e custo operacional. "
            "Os resultados contribuirão para o estabelecimento de melhores práticas de "
            "arquitetura e operação de sistemas distribuídos em nuvem."
        ),
        "lattes_id": "2847165039284716",
        "autores": "Bianca Siqueira Pacheco, Emanuel Costa Freitas, Renato Alves Gonçalves"
    },
    23: {
        "titulo": "Segurança em Redes IoT: Criptografia e Mitigação de Vulnerabilidades",
        "descricao": (
            "A proliferação de dispositivos conectados à Internet das Coisas (IoT) em ambientes "
            "industriais e domésticos amplia significativamente a superfície de ataque a "
            "infraestruturas críticas. Este projeto propõe o desenvolvimento de um framework "
            "de segurança para redes IoT, integrando mecanismos de criptografia leve, "
            "autenticação mútua e detecção de anomalias baseada em aprendizado de máquina. "
            "A pesquisa incluirá a criação de um ambiente de testbed com dispositivos IoT "
            "heterogêneos, a realização de testes de penetração para identificação de "
            "vulnerabilidades e a proposta de contramedidas. Serão avaliados algoritmos "
            "criptográficos adequados às restrições de processamento e energia dos dispositivos "
            "IoT, como PRESENT, SIMON e SPECK. O framework será validado em cenários simulados "
            "de ataques reais documentados na literatura, como ataques DDoS, injeção de "
            "comandos e interceptação de comunicação."
        ),
        "lattes_id": "6031847592648301",
        "autores": "Carolina Andrade Melo, Fábio Luiz Correia, Tatiana Borges Rezende"
    },
    24: {
        "titulo": "Redes Neurais Convolucionais para Reconhecimento de Imagens Médicas",
        "descricao": (
            "O diagnóstico por imagem representa uma das áreas mais promissoras para a aplicação "
            "de deep learning na medicina. Este projeto desenvolve e avalia arquiteturas de redes "
            "neurais convolucionais (CNN) para a classificação automática de lesões dermatológicas "
            "em imagens de dermatoscopia, com foco na distinção entre melanoma e lesões benignas. "
            "O dataset de treinamento será composto por mais de 50.000 imagens rotuladas por "
            "dermatologistas especialistas, provenientes de bases públicas internacionais e "
            "de parceiros clínicos brasileiros. Serão exploradas técnicas de transfer learning "
            "com modelos pré-treinados em ImageNet (ResNet, EfficientNet, Vision Transformer) "
            "e estratégias de data augmentation para lidar com o desbalanceamento de classes. "
            "A avaliação dos modelos incluirá análise de sensibilidade e especificidade por "
            "nível de gravidade da lesão, além de análise de viés demográfico nos resultados."
        ),
        "lattes_id": "9284731605928473",
        "autores": "Daniel Ferreira Campos, Giovana Martins Pereira, Sérgio Luiz Ramos"
    },
    25: {
        "titulo": "Bancos de Dados em Grafos: Otimização de Consultas e Inferência Semântica",
        "descricao": (
            "Os bancos de dados em grafos têm emergido como solução eficaz para modelar e consultar "
            "dados altamente conectados em domínios como redes sociais, bioinformática e sistemas "
            "de recomendação. Este projeto investiga técnicas de otimização de consultas em "
            "grafos de conhecimento de larga escala, com foco em consultas SPARQL sobre dados "
            "ligados (Linked Data). A pesquisa propõe novos índices e estratégias de execução "
            "de consultas que exploram a estrutura semântica dos grafos para reduzir o espaço "
            "de busca. Serão desenvolvidos algoritmos de inferência baseados em regras ontológicas "
            "para enriquecimento automático dos grafos de conhecimento. Os experimentos utilizarão "
            "benchmarks padronizados (BSBM, LUBM, WatDiv) e grafos de conhecimento reais do "
            "domínio biomédico. Os resultados contribuirão para a melhoria do desempenho de "
            "sistemas de recuperação de informação semântica em larga escala."
        ),
        "lattes_id": "3748019265473801",
        "autores": "Eliane Cristina Souza, Hugo Menezes Carvalho, Verônica Abreu Dias"
    },
    26: {
        "titulo": "Análise de Sentimentos em Redes Sociais com Processamento de Linguagem Natural",
        "descricao": (
            "O monitoramento de opiniões e sentimentos expressos em redes sociais possui aplicações "
            "em diversas áreas, desde marketing e comunicação política até vigilância em saúde pública. "
            "Este projeto desenvolve modelos de análise de sentimentos para textos em português "
            "brasileiro, com foco no contexto das redes sociais digitais. A pesquisa inclui a "
            "construção de um corpus anotado de 100.000 tweets e posts sobre temas de saúde pública, "
            "com anotação manual de polaridade e emoções por múltiplos anotadores. Serão treinados "
            "e comparados modelos baseados em embeddings contextuais (BERTimbau, RoBERTa-pt) "
            "e abordagens de few-shot learning com LLMs. A avaliação abrangerá a robustez "
            "dos modelos a fenômenos linguísticos típicos das redes sociais, como ironia, "
            "gírias e neologismos. Os recursos linguísticos produzidos serão disponibilizados "
            "publicamente para a comunidade científica."
        ),
        "lattes_id": "5910284736591028",
        "autores": "Flávia Rocha Nunes, Ivã Luís Torres, Wendell Augusto Barros"
    },
    27: {
        "titulo": "Planejamento de Trajetórias para Robótica Autônoma em Ambientes Dinâmicos",
        "descricao": (
            "O planejamento de trajetórias em tempo real é um desafio fundamental para robôs autônomos "
            "que operam em ambientes compartilhados com humanos e outros agentes dinâmicos. "
            "Este projeto propõe algoritmos de planejamento de movimento que combinam técnicas de "
            "busca heurística (A*, D* Lite) com aprendizado por reforço profundo para lidar com "
            "a incerteza e a dinamicidade dos ambientes reais. Os algoritmos serão desenvolvidos "
            "e testados em simulação (Gazebo/ROS2) e validados em uma plataforma robótica móvel "
            "instrumentada com câmeras RGBD e LiDAR. Os cenários de teste incluem corredores "
            "com obstáculos móveis, ambientes semi-estruturados e situações de emergência "
            "com replanejamento instantâneo. O desempenho será avaliado em termos de tempo "
            "de planejamento, distância percorrida, taxa de colisão e suavidade das trajetórias. "
            "Os códigos e datasets gerados serão disponibilizados como software open source."
        ),
        "lattes_id": "8142037956814203",
        "autores": "Guilherme Pedroso Lima, Nathalia Cristina Fonseca, Yuri Barbosa Almeida"
    },
    28: {
        "titulo": "Acessibilidade em Aplicativos Mobile para Deficientes Visuais",
        "descricao": (
            "A acessibilidade digital é um direito fundamental que possibilita a participação plena "
            "de pessoas com deficiência na sociedade digital. Este projeto avalia as barreiras de "
            "acessibilidade em aplicativos móveis de serviços públicos essenciais (saúde, transporte "
            "e educação) para usuários com deficiência visual, propondo diretrizes e soluções "
            "baseadas em evidências. A metodologia inclui avaliação heurística com especialistas "
            "em acessibilidade, testes de usabilidade com 30 usuários cegos ou com baixa visão "
            "utilizando leitores de tela (TalkBack/VoiceOver), e análise automatizada de "
            "conformidade com as diretrizes WCAG 2.1. Com base nos resultados, serão propostas "
            "e prototipadas melhorias em interfaces selecionadas, avaliando o impacto das "
            "modificações em nova rodada de testes com usuários. O projeto também envolve "
            "a capacitação de desenvolvedores de software em práticas de desenvolvimento "
            "acessível por meio de workshops e material didático produzido pela equipe."
        ),
        "lattes_id": "1736094852173609",
        "autores": "Helena Vieira Cardoso, Leandro Pinto Mendes, Zélia Aparecida Monteiro"
    },
    29: {
        "titulo": "Blockchain e Contratos Inteligentes para Rastreabilidade na Cadeia do Agronegócio",
        "descricao": (
            "A rastreabilidade de produtos agroalimentares é essencial para garantir a segurança "
            "do consumidor e a conformidade com regulamentações sanitárias e ambientais. "
            "Este projeto propõe uma arquitetura baseada em blockchain e contratos inteligentes "
            "para rastreabilidade da cadeia produtiva do café especial, desde a fazenda até "
            "o consumidor final. A solução utilizará a plataforma Hyperledger Fabric e integrará "
            "dados de sensores IoT instalados em lavouras, cooperativas e torrefadoras parceiras. "
            "Os contratos inteligentes automatizarão a validação e o registro de eventos relevantes "
            "da cadeia, como aplicação de defensivos, colheita, processamento e transporte. "
            "Um aplicativo mobile permitirá que consumidores rastreiem o histórico completo do "
            "produto via QR code. O projeto será desenvolvido em parceria com a Cooperativa "
            "de Cafeicultores do Sul de Minas, envolvendo 50 produtores na fase piloto."
        ),
        "lattes_id": "4859271036485927",
        "autores": "Ian Marcelo Freitas, Melissa Duarte Costa, Otávio Luiz Alencar"
    },
    30: {
        "titulo": "Internet das Coisas para Monitoramento Ambiental em Zonas Urbanas",
        "descricao": (
            "O monitoramento contínuo de variáveis ambientais em zonas urbanas é fundamental para "
            "subsidiar políticas de gestão ambiental e saúde pública. Este projeto desenvolve "
            "uma rede de sensores sem fio de baixo custo baseada em IoT para monitoramento "
            "em tempo real de qualidade do ar (PM2.5, PM10, NOx, O3, CO), ruído e temperatura "
            "em 20 pontos distribuídos pelo município de Belo Horizonte. A arquitetura da rede "
            "utiliza o protocolo LoRaWAN para comunicação de longa distância com baixo consumo "
            "energético. Os dados são transmitidos a uma plataforma de análise em nuvem que "
            "aplica algoritmos de detecção de anomalias e gera mapas de exposição ambiental "
            "com atualização horária. O projeto inclui validação dos sensores de baixo custo "
            "em comparação com estações de referência certificadas. Os dados serão disponibilizados "
            "em formato aberto para pesquisadores, gestores públicos e a população em geral."
        ),
        "lattes_id": "7021364895702136",
        "autores": "Jéssica Tavares Gomes, Pedro Henrique Lemos, Raquel Pires Borges"
    },

    # ---- BLOCO 4: IDs 31-40 (Agronomia) -----------------------------------
    31: {
        "titulo": "Melhoramento Genético da Soja para Tolerância à Seca em Regiões Tropicais",
        "descricao": (
            "A soja é a principal oleaginosa cultivada no Brasil, ocupando mais de 40 milhões de "
            "hectares e respondendo por parcela significativa das exportações agropecuárias. "
            "Os eventos de seca associados às variações climáticas têm causado perdas crescentes "
            "na produtividade da cultura, motivando o desenvolvimento de genótipos mais tolerantes "
            "ao estresse hídrico. Este projeto avalia 250 linhagens avançadas de soja do programa "
            "de melhoramento da Embrapa Soja quanto à tolerância à seca em fase reprodutiva, "
            "em experimentos conduzidos em telado com controle de irrigação. As avaliações incluem "
            "parâmetros agronômicos (produção de grãos, número de vagens, peso de cem sementes) "
            "e fisiológicos (índice SPAD, fluorescência, potencial hídrico foliar). "
            "Os marcadores moleculares SNP associados às regiões genômicas de tolerância serão "
            "mapeados para subsidiar a seleção assistida por marcadores. As linhagens mais "
            "promissoras avançarão para ensaios de valor de cultivo e uso (VCU) regionais."
        ),
        "lattes_id": "3847201965384720",
        "autores": "Adriano Costa Vilela, Beatriz Ferreira Moura, Reinaldo Gomes Viana"
    },
    32: {
        "titulo": "Controle Biológico da Broca-do-Café com Nematoides Entomopatogênicos",
        "descricao": (
            "A broca-do-café (Hypothenemus hampei) é a principal praga da cafeicultura mundial, "
            "causando perdas que podem superar 30% da produção em anos de alta infestação. "
            "O controle biológico com nematoides entomopatogênicos representa uma alternativa "
            "sustentável ao uso de inseticidas químicos. Este projeto seleciona e avalia a "
            "eficácia de isolados nativos dos nematoides Steinernema spp. e Heterorhabditis spp. "
            "para o controle da broca-do-café em condições de laboratório, semicampo e campo. "
            "Serão testados formulações à base de polvilho e alginato para otimização da "
            "sobrevivência e dispersão dos nematoides em campo. A compatibilidade dos nematoides "
            "com outros insumos do manejo integrado de pragas do café será avaliada. "
            "Os experimentos de campo serão conduzidos em lavouras de café arábica convencional "
            "e orgânica no sul de Minas Gerais, com monitoramento da infestação e avaliação "
            "da qualidade da bebida produzida nos tratamentos."
        ),
        "lattes_id": "6192038475619203",
        "autores": "Carla Meireles Pinheiro, Eduardo Tadeu Borges, Solange Cristina Ramos"
    },
    33: {
        "titulo": "Transição Agroecológica em Sistemas Familiares do Sul do Brasil",
        "descricao": (
            "A agricultura familiar tem papel central na produção de alimentos para o mercado interno "
            "brasileiro, mas enfrenta desafios relacionados à sustentabilidade ambiental e econômica "
            "dos sistemas produtivos convencionais. Este projeto acompanha o processo de transição "
            "agroecológica em 40 propriedades familiares de agricultura convencional para sistemas "
            "de base agroecológica nos municípios de Laranjeiras do Sul e Cantagalo, no Paraná. "
            "A pesquisa adota abordagem participativa, com agricultores como protagonistas do processo "
            "de inovação. Serão avaliados indicadores de sustentabilidade nas dimensões econômica, "
            "ambiental, social e cultural ao longo de 3 anos de transição. Os serviços ecossistêmicos "
            "promovidos pelos sistemas agroecológicos, como regulação do ciclo da água, controle "
            "de erosão e promoção da biodiversidade, serão quantificados e valorados. "
            "Os resultados subsidiarão políticas públicas de extensão rural e assistência técnica "
            "para a transição agroecológica na região."
        ),
        "lattes_id": "9284756103928475",
        "autores": "David Soares Magalhães, Fernanda Cristina Lago, Valdirene Aparecida Sousa"
    },
    34: {
        "titulo": "Manejo Eficiente da Água em Solos Arenosos do Semiárido do Nordeste",
        "descricao": (
            "A escassez hídrica no semiárido nordestino exige o desenvolvimento de estratégias "
            "eficientes de uso da água para a viabilização da produção agrícola sustentável. "
            "Este projeto avalia o desempenho de sistemas de irrigação localizada (gotejamento "
            "e microaspersão) em solos de textura arenosa do Sertão pernambucano, para a "
            "cultura da goiabeira (Psidium guajava) em sistema orgânico. Serão avaliados "
            "diferentes lâminas de irrigação (40, 60, 80 e 100% da evapotranspiração de referência) "
            "e intervalos de aplicação (diário e a cada dois dias) sobre o desenvolvimento das "
            "plantas, produtividade, qualidade dos frutos e eficiência de uso da água. "
            "O monitoramento do balanço hídrico do solo será realizado por tensiômetros e sondas "
            "de capacitância. Os resultados contribuirão para o estabelecimento de critérios "
            "de manejo da irrigação que maximizem a produtividade da água em condições "
            "edafoclimáticas típicas do semiárido nordestino."
        ),
        "lattes_id": "2037485619203748",
        "autores": "Elisa Moreno Cavalcanti, Guilherme Prado Siqueira, Wania Fátima Melo"
    },
    35: {
        "titulo": "Qualidade Pós-Colheita e Armazenamento Refrigerado de Manga Tommy Atkins",
        "descricao": (
            "A manga (Mangifera indica) é uma das principais frutas tropicais exportadas pelo Brasil, "
            "com o Vale do São Francisco respondendo por mais de 90% das exportações nacionais. "
            "A manutenção da qualidade durante o armazenamento refrigerado e o transporte é "
            "determinante para a competitividade no mercado internacional. Este projeto avalia "
            "o efeito de diferentes temperaturas de armazenamento (8, 10 e 12°C), atmósferas "
            "modificadas e tratamentos pós-colheita com cera carnaúba e 1-metilciclopropeno (1-MCP) "
            "sobre a qualidade físico-química, sensorial e nutricional de mangas cv. Tommy Atkins. "
            "Serão avaliados firmeza da polpa, sólidos solúveis, acidez titulável, cor da casca, "
            "incidência de podridões, perfil de ácidos graxos e teor de carotenoides ao longo de "
            "21 dias de armazenamento. Os resultados orientarão o estabelecimento de protocolos "
            "pós-colheita para extensão da vida útil das mangas exportadas."
        ),
        "lattes_id": "5193847261059384",
        "autores": "Fábio Ramos Azevedo, Letícia Borges Henrique, Ubiraci Alves Neto"
    },
    36: {
        "titulo": "Manejo Integrado de Doenças Fúngicas do Trigo no Sul do Brasil",
        "descricao": (
            "A ferrugem da folha (Puccinia triticina), a giberela (Fusarium graminearum) e a mancha "
            "amarela (Drechslera tritici-repentis) são as principais doenças fúngicas do trigo "
            "no Sul do Brasil, causando perdas anuais que variam entre 20 e 70% da produção. "
            "Este projeto avalia a eficácia de fungicidas multissítio e específicos aplicados "
            "em diferentes estádios fenológicos da cultura sobre a intensidade das doenças, "
            "produtividade e qualidade dos grãos (teor de proteína, peso hectolítrico, "
            "índice de falling number). Serão conduzidos experimentos em 6 municípios do "
            "Rio Grande do Sul e do Paraná, em cultivares com diferentes perfis de resistência. "
            "A viabilidade econômica das estratégias de manejo será calculada com base na "
            "relação custo/benefício dos tratamentos. Os resultados contribuirão para a "
            "atualização das recomendações técnicas de manejo de doenças para as cultivares "
            "de trigo cultivadas na região."
        ),
        "lattes_id": "8740392651874039",
        "autores": "Gisele Aparecida Farias, Marco Aurélio Rezende, Teresinha Gomes Duarte"
    },
    37: {
        "titulo": "Sequestro de Carbono no Solo em Sistemas de Plantio Direto Consolidado",
        "descricao": (
            "O plantio direto é o sistema de manejo do solo dominante na agricultura brasileira, "
            "cobrindo mais de 35 milhões de hectares. Uma das principais vantagens apregoadas "
            "ao sistema é seu potencial de sequestro de carbono orgânico no solo. Este projeto "
            "quantifica os estoques de carbono orgânico total e suas frações (lábeis e estáveis) "
            "em sistemas de plantio direto com diferentes idades de implantação (5, 10, 20 e "
            "30 anos) e rotações de culturas, em Latossolos do Paraná e Rio Grande do Sul. "
            "As amostragens serão realizadas em perfis de 0-100 cm de profundidade, com análise "
            "de carbono orgânico total, nitrogênio total, carbono da biomassa microbiana e "
            "fracionamento da matéria orgânica. Os resultados permitirão estimar as taxas anuais "
            "de acúmulo de carbono em diferentes cenários de manejo e subsidiar a elaboração "
            "de inventários de emissões e remoções de GEE no setor agropecuário brasileiro."
        ),
        "lattes_id": "1958274036195827",
        "autores": "Hugo Ferreira Campos, Nara Cristina Andrade, Patrícia Souza Lima"
    },
    38: {
        "titulo": "Qualidade Enológica de Vinhos Finos das Regiões de Altitude de SC",
        "descricao": (
            "O estado de Santa Catarina possui uma viticultura emergente nas regiões de altitude "
            "da Serra Gaúcha e do Planalto Catarinense, com potencial reconhecido para a "
            "produção de vinhos finos de qualidade superior. Este projeto avalia o perfil "
            "físico-químico, sensorial e metabolômico de vinhos tintos e brancos elaborados com "
            "cultivares Vitis vinifera (Cabernet Sauvignon, Merlot, Chardonnay, Riesling Itálico) "
            "em vinícolas das regiões de São Joaquim e Campos Novos. As análises incluem "
            "parâmetros enológicos clássicos, perfil de antocianinas, compostos fenólicos totais, "
            "ácidos orgânicos e álcoois por cromatografia de alta eficiência. A análise sensorial "
            "será conduzida por painel treinado e análise descritiva quantitativa. "
            "Os resultados contribuirão para o estabelecimento de indicadores de tipicidade "
            "e denominação de origem dos vinhos catarinenses de altitude."
        ),
        "lattes_id": "4063819274060381",
        "autores": "Igor Machado Ribeiro, Olga Regina Santos, Sabrina Melo Torres"
    },
    39: {
        "titulo": "Nutrição e Suplementação Proteica em Bovinos de Corte em Pastagem",
        "descricao": (
            "O Brasil possui o maior rebanho comercial bovino do mundo, com a pecuária de corte "
            "baseada predominantemente em sistemas extensivos de pastagem. A suplementação "
            "proteico-energética na seca é uma estratégia consolidada para manter o desempenho "
            "animal nos períodos de baixa qualidade nutritiva das forrageiras. Este projeto "
            "avalia o efeito de diferentes fontes e níveis de proteína metabolizável (ureia, "
            "farelo de soja e torta de girassol) em suplementos minerais sobre o desempenho "
            "de bovinos Nelore em pastagens de Brachiaria brizantha cv. Marandu durante "
            "o período seco. Serão avaliados ganho de peso médio diário, conversão alimentar, "
            "escore de condição corporal, digestibilidade dos nutrientes e perfil metabólico sanguíneo. "
            "A análise econômica dos tratamentos considerará o custo da suplementação versus "
            "o ganho de peso adicional obtido, em diferentes cenários de preço do boi gordo."
        ),
        "lattes_id": "7281934605728193",
        "autores": "Jonas Pereira Coelho, Miriam Aparecida Cruz, Wilton Rodrigues Barros"
    },
    40: {
        "titulo": "Qualidade Fisiológica de Sementes de Soja em Diferentes Condições de Armazenamento",
        "descricao": (
            "A manutenção da qualidade fisiológica das sementes durante o armazenamento é fundamental "
            "para garantir o estabelecimento adequado das lavouras e a produtividade das culturas. "
            "Este projeto avalia o efeito de diferentes condições de armazenamento (temperatura "
            "de 10, 20 e 30°C; umidade relativa de 50, 65 e 75%) sobre a qualidade fisiológica "
            "de sementes de soja (cv. BRS 360RR e M-8210 IPRO) ao longo de 12 meses. "
            "Serão realizados testes de germinação, vigor (envelhecimento acelerado, frio, "
            "tetrazólio), teor de água, condutividade elétrica e sanidade a cada dois meses. "
            "Os resultados das análises serão correlacionados com a performance das sementes "
            "em campo sob diferentes condições de semeadura. Modelos matemáticos de deterioração "
            "serão ajustados para predizer a longevidade das sementes em diferentes condições "
            "de armazenamento, com implicações para o manejo de estoques em unidades "
            "beneficiadoras de sementes."
        ),
        "lattes_id": "3048271956304827",
        "autores": "Katia Lucia Fonseca, Raimundo Pereira Neto, Valéria Cristina Matos"
    },

    # ---- BLOCO 5: IDs 41-50 (Saúde) --------------------------------------
    41: {
        "titulo": "Prevalência e Fatores de Risco do Diabetes Tipo 2 em Adultos Urbanos",
        "descricao": (
            "O diabetes mellitus tipo 2 é uma das doenças crônicas de maior impacto em saúde pública "
            "no Brasil, com estimativa de 16 milhões de adultos afetados e tendência crescente. "
            "Este projeto realiza um estudo epidemiológico de corte transversal para estimar a "
            "prevalência de diabetes tipo 2 e dos fatores de risco associados em adultos de 30 a "
            "69 anos residentes em 4 municípios de médio porte do interior de São Paulo. "
            "Uma amostra probabilística de 2.400 adultos será submetida a entrevistas estruturadas, "
            "avaliação antropométrica, aferição de pressão arterial e coleta de sangue para "
            "dosagem de glicemia de jejum, hemoglobina glicada, perfil lipídico e insulina basal. "
            "Os fatores de risco investigados incluem histórico familiar, obesidade abdominal, "
            "sedentarismo, alimentação inadequada, hipertensão e dislipidemia. "
            "Os resultados contribuirão para o planejamento de ações de prevenção e controle "
            "do diabetes na atenção primária à saúde dos municípios participantes."
        ),
        "lattes_id": "6192847305062938",
        "autores": "Larissa Moraes Cunha, Paulo Sérgio Vasconcelos, Silvana Batista Rocha"
    },
    42: {
        "titulo": "Intervenção Psicossocial para Depressão em Adolescentes Escolares",
        "descricao": (
            "A depressão na adolescência é um problema de saúde mental subestimado e subtratado, "
            "com consequências negativas sobre o desenvolvimento, o desempenho escolar e a "
            "qualidade de vida dos jovens afetados. Este projeto avalia a eficácia de um "
            "programa de intervenção psicossocial em grupo, baseado em terapia cognitivo-comportamental "
            "adaptada para adolescentes, aplicado em 10 escolas públicas de Recife. "
            "Um total de 300 adolescentes de 14 a 18 anos com sintomas depressivos moderados "
            "serão randomizados em grupo intervenção e grupo controle (lista de espera). "
            "A intervenção consiste em 12 sessões semanais conduzidas por psicólogos treinados. "
            "Os desfechos primários incluem escores de depressão (PHQ-A) e qualidade de vida "
            "(KIDSCREEN-52), avaliados no início, ao final da intervenção e após 6 meses. "
            "Os resultados orientarão a elaboração de um protocolo de intervenção em saúde mental "
            "escolar adaptado ao contexto brasileiro para replicação em larga escala."
        ),
        "lattes_id": "9374850162937485",
        "autores": "Márcio Luiz Teixeira, Raíssa Andrade Nunes, Túlio Henrique Correia"
    },
    43: {
        "titulo": "Resistência Bacteriana a Antibióticos em Infecções Hospitalares do Nordeste",
        "descricao": (
            "A resistência antimicrobiana representa uma das maiores ameaças à saúde pública global, "
            "com crescente prevalência de bactérias multirresistentes em ambientes hospitalares "
            "brasileiros. Este projeto caracteriza o perfil de resistência de isolados bacterianos "
            "de infecções relacionadas à assistência à saúde (IRAS) em 5 hospitais de grande "
            "porte do Nordeste, com ênfase em Staphylococcus aureus resistente à meticilina (MRSA), "
            "Klebsiella pneumoniae produtora de carbapenemase (KPC) e Acinetobacter baumannii. "
            "As análises incluem antibiograma por disco-difusão e CIM, pesquisa de genes de "
            "resistência por PCR e sequenciamento de genoma completo de isolados selecionados "
            "para análise da epidemiologia molecular e das rotas de transmissão. "
            "Os resultados alimentarão um sistema de vigilância integrada da resistência "
            "antimicrobiana, com emissão de alertas em tempo real para os hospitais participantes "
            "e para os órgãos de saúde pública estaduais."
        ),
        "lattes_id": "2847163950284716",
        "autores": "Natália Bentes Araújo, Osvaldo Luiz Prado, Yolanda Cristina Freitas"
    },
    44: {
        "titulo": "Cuidados Paliativos e Manejo da Dor em Pacientes Oncológicos Hospitalizados",
        "descricao": (
            "Os cuidados paliativos visam melhorar a qualidade de vida de pacientes com doenças "
            "ameaçadoras da vida por meio da prevenção e alívio do sofrimento. O manejo adequado "
            "da dor oncológica é um dos principais desafios nesse contexto. Este projeto avalia "
            "a implantação de um protocolo sistematizado de avaliação e manejo da dor baseado "
            "na escada analgésica da OMS em uma unidade de oncologia de hospital universitário "
            "do Sul do Brasil. O estudo compara indicadores de qualidade assistencial (proporção "
            "de pacientes com dor avaliada, adequação das prescrições analgésicas, satisfação "
            "dos pacientes) antes e após a implantação do protocolo. A equipe de enfermagem "
            "receberá treinamento intensivo em avaliação da dor e manejo farmacológico e "
            "não farmacológico. Uma coorte prospectiva de 180 pacientes internados será "
            "acompanhada por 6 meses, com coleta semanal de dados sobre intensidade da dor, "
            "consumo de analgésicos e qualidade de vida."
        ),
        "lattes_id": "5930184726593018",
        "autores": "Otília Fernandes Guimarães, Pedro Augusto Braga, Regina Maria Andrade"
    },
    45: {
        "titulo": "Vigilância Entomológica e Controle Vetorial da Dengue em Municípios do Interior do CE",
        "descricao": (
            "A dengue, a zika e a chikungunya são arboviroses transmitidas pelo Aedes aegypti "
            "que representam grave problema de saúde pública no Brasil, especialmente no Nordeste. "
            "Este projeto implementa um sistema de vigilância entomológica aprimorado, integrando "
            "armadilhas Ovitrap, BG-Sentinel e monitoramento com drones em 6 municípios do "
            "interior do Ceará com histórico de surtos de dengue. Os dados entomológicos serão "
            "correlacionados com condições climáticas e de saneamento para modelagem preditiva "
            "de surtos. Com base nos resultados do monitoramento, serão testadas estratégias "
            "integradas de controle vetorial, incluindo liberação de machos estéreis, aplicação "
            "de Bacillus thuringiensis israelensis (Bti) em focos e mobilização comunitária "
            "direcionada. A efetividade das estratégias será avaliada pela redução dos índices "
            "entomológicos e pela incidência de casos nas áreas de intervenção."
        ),
        "lattes_id": "8471926350847192",
        "autores": "Patrícia Neves Rocha, Sandro Luiz Gonçalves, Wilma Cristina Lemos"
    },
    46: {
        "titulo": "Suporte Nutricional e Desnutrição em Pacientes Clínicos Hospitalizados",
        "descricao": (
            "A desnutrição hospitalar é uma condição prevalente e frequentemente subdiagnosticada, "
            "associada a piores desfechos clínicos, maior tempo de internação e elevação dos "
            "custos hospitalares. Este projeto avalia a prevalência de desnutrição e risco "
            "nutricional em pacientes adultos internados em enfermarias clínicas de 3 hospitais "
            "gerais de Belém do Pará, utilizando as ferramentas de triagem NRS-2002 e MUST. "
            "Os pacientes identificados com risco nutricional serão randomizados para intervenção "
            "de suporte nutricional individualizado (suplementação oral, enteral ou parenteral) "
            "versus cuidado nutricional convencional. Os desfechos avaliados incluem estado "
            "nutricional ao longo da internação, tempo de internação, complicações infecciosas "
            "e mortalidade intra-hospitalar. Os resultados subsidiarão a implantação de "
            "uma rotina sistematizada de triagem e intervenção nutricional nos hospitais participantes."
        ),
        "lattes_id": "1746385021174638",
        "autores": "Quitéria Aparecida Mota, Rodrigo Siqueira Campos, Tereza Cristina Braga"
    },
    47: {
        "titulo": "Reabilitação Neuromotora Pós-AVC por Estimulação e Fisioterapia Intensiva",
        "descricao": (
            "O acidente vascular cerebral (AVC) é a principal causa de incapacidade adquirida "
            "em adultos no Brasil. A neuroplasticidade cerebral permite recuperação funcional "
            "significativa quando a reabilitação é iniciada precocemente e de forma intensiva. "
            "Este projeto avalia o impacto de um protocolo de fisioterapia neurológica intensiva "
            "combinado com estimulação magnética transcraniana repetitiva (EMTr) sobre a "
            "recuperação motora de membros superiores em pacientes com AVC isquêmico de até "
            "6 meses de evolução. Um ensaio clínico randomizado duplo-cego será conduzido "
            "com 80 pacientes, comparando o protocolo combinado com fisioterapia convencional. "
            "Os desfechos funcionais incluem escalas de Fugl-Meyer, Barthel e NIHSS, avaliados "
            "no início, ao final do tratamento (8 semanas) e após 3 meses de seguimento. "
            "Exames de neuroimagem funcional (fMRI) em subgrupo de pacientes documentarão "
            "as mudanças na reorganização cortical induzidas pela intervenção."
        ),
        "lattes_id": "4920183756492018",
        "autores": "Roberto Carlos Assis, Sandra Patrícia Mendes, Ulisses Faria Moreira"
    },
    48: {
        "titulo": "Fluoretação da Água e Prevalência de Cárie e Fluorose em Crianças",
        "descricao": (
            "A fluoretação das águas de abastecimento público é considerada uma das medidas de "
            "saúde pública de maior custo-efetividade para a prevenção da cárie dentária. "
            "Este projeto investiga a associação entre os teores de flúor nas águas distribuídas "
            "e a prevalência de cárie (índice CPO-D) e fluorose dentária (índice TF) em escolares "
            "de 12 anos de 20 municípios do Estado do Ceará com diferentes históricos de "
            "fluoretação da água. Serão examinados 2.000 escolares, coletadas amostras de água "
            "em pontos de abastecimento e realizadas entrevistas com pais ou responsáveis sobre "
            "exposição ao flúor (dentifrícios, suplementos, alimentos). Os resultados permitirão "
            "identificar os municípios com níveis de flúor inadequados (abaixo de 0,6 ou "
            "acima de 0,9 mg/L) e subsidiar ações de controle operacional dos sistemas "
            "de fluoretação pelo Programa de Vigilância da Qualidade da Água para Consumo Humano."
        ),
        "lattes_id": "7183064592718306",
        "autores": "Samara Luiza Borges, Valentim Costa Neves, Yara Beatriz Machado"
    },
    49: {
        "titulo": "Rastreamento e Controle da Hipertensão Arterial na Atenção Primária",
        "descricao": (
            "A hipertensão arterial sistêmica é o principal fator de risco cardiovascular no Brasil, "
            "afetando aproximadamente 36% da população adulta. O controle inadequado da pressão "
            "arterial na atenção primária é reconhecido como um dos grandes desafios do sistema "
            "de saúde. Este projeto implementa e avalia um modelo de cuidado colaborativo para "
            "rastreamento e controle da hipertensão em 15 Unidades de Saúde da Família de "
            "Porto Alegre, envolvendo equipes multiprofissionais com médicos, enfermeiros, "
            "farmacêuticos e agentes comunitários de saúde. A intervenção inclui rastreamento "
            "oportunístico de hipertensão, consultas de enfermagem protocoladas, telemonitoramento "
            "da pressão arterial domiciliar e aplicativo de smartphone para adesão ao tratamento. "
            "Os desfechos primários são a proporção de pacientes com pressão arterial controlada "
            "(< 140/90 mmHg) e a adesão ao tratamento medicamentoso, avaliados em seguimento "
            "de 12 meses."
        ),
        "lattes_id": "3047182936304718",
        "autores": "Tássia Rodrigues Feitosa, Vinícius Almeida Pinheiro, Zuleide Aparecida Costa"
    },
    50: {
        "titulo": "Diagnóstico Molecular por PCR em Tempo Real de Arboviroses Tropicais",
        "descricao": (
            "O diagnóstico laboratorial precoce e preciso das arboviroses (dengue, zika, chikungunya, "
            "febre amarela) é essencial para o manejo clínico adequado e para a resposta oportuna "
            "de vigilância epidemiológica. Este projeto desenvolve e valida painéis de PCR em "
            "tempo real multiplex para detecção simultânea dos principais arbovírus circulantes "
            "no Brasil, utilizando amostras de soro, sangue total e urina. Primers e sondas TaqMan "
            "específicos para cada arbovírus serão desenhados em regiões conservadas do genoma "
            "viral, com avaliação de especificidade frente a outros vírus de diagnóstico diferencial. "
            "A sensibilidade analítica e diagnóstica será avaliada em painéis de amostras "
            "caracterizadas de pacientes com diagnóstico confirmado de cada arbovirose, "
            "provenientes de biobancos de unidades de referência de infectologia do Nordeste. "
            "Os protocolos otimizados serão transferidos para laboratórios da rede pública "
            "de saúde dos estados participantes."
        ),
        "lattes_id": "6291847305629184",
        "autores": "Ursula Helena Carvalho, Wesley Batista Rezende, Ângela Cristina Dias"
    },

    # ---- BLOCO 6: IDs 51-60 (Ciências Sociais) ----------------------------
    51: {
        "titulo": "Segregação Habitacional e Desigualdade Social em Metrópoles Brasileiras",
        "descricao": (
            "A segregação residencial é um fenômeno estruturante das desigualdades urbanas no Brasil, "
            "reproduzindo condições diferenciadas de acesso a serviços, equipamentos públicos e "
            "oportunidades de emprego segundo a localização da moradia. Este projeto analisa os "
            "padrões de segregação habitacional em três regiões metropolitanas brasileiras (São Paulo, "
            "Salvador e Fortaleza), investigando suas articulações com dinâmicas de mercado "
            "imobiliário, políticas habitacionais e mobilidade social. A metodologia combina análise "
            "espacial de microdados do Censo Demográfico, levantamentos de campo em assentamentos "
            "precários e condomínios fechados, e entrevistas em profundidade com moradores, "
            "gestores públicos e agentes do mercado imobiliário. Os resultados contribuirão para "
            "a compreensão das dinâmicas de reprodução das desigualdades urbanas e para a "
            "formulação de políticas habitacionais mais equitativas e inclusivas."
        ),
        "lattes_id": "8473920165847392",
        "autores": "Álvaro Mendes Fonseca, Bruna Lopes Cavalcanti, Caio Rodrigues Vieira"
    },
    52: {
        "titulo": "Identidade, Território e Direitos dos Povos Indígenas no Brasil Central",
        "descricao": (
            "Os povos indígenas do Brasil Central enfrentam crescentes ameaças à integridade de "
            "seus territórios e ao exercício de seus direitos constitucionalmente garantidos, "
            "em contexto de avanço do agronegócio e de enfraquecimento dos órgãos indigenistas. "
            "Este projeto realiza pesquisa etnográfica com três povos do Mato Grosso do Sul — "
            "Terena, Guarani-Kaiowá e Kadiwéu — investigando as estratégias de resistência "
            "e reafirmação identitária diante das pressões sobre suas terras e modos de vida. "
            "A metodologia inclui observação participante de longa duração, entrevistas "
            "com lideranças e anciãos, análise de documentos jurídicos e acompanhamento "
            "de processos de demarcação territorial em curso. O projeto produzirá relatórios "
            "técnicos de suporte aos processos de demarcação e publicações acadêmicas sobre "
            "a situação fundiária e os direitos indígenas nos contextos estudados."
        ),
        "lattes_id": "2916384750291638",
        "autores": "Denise Cristina Pinto, Everton Luís Gomes, Fátima Borges Souza"
    },
    53: {
        "titulo": "Direitos Fundamentais e Controle de Constitucionalidade no STF",
        "descricao": (
            "O Supremo Tribunal Federal (STF) tem exercido papel crescente na conformação das "
            "políticas públicas brasileiras por meio do controle de constitucionalidade. "
            "Este projeto analisa a jurisprudência do STF em matéria de direitos fundamentais "
            "sociais — saúde, educação, moradia e assistência social — no período de 2005 a 2023, "
            "investigando os padrões de argumentação jurídica, os efeitos das decisões sobre "
            "as políticas públicas e os limites do ativismo judicial. A pesquisa adota "
            "metodologia de análise documental com técnicas de jurimetria para o mapeamento "
            "quantitativo e qualitativo das decisões, complementada por entrevistas com "
            "ministros, procuradores e gestores públicos. Os resultados contribuirão para "
            "o debate sobre os limites e possibilidades da judicialização de políticas sociais "
            "e para a formulação de parâmetros de racionalidade nas decisões judiciais "
            "sobre direitos fundamentais."
        ),
        "lattes_id": "5047281936504728",
        "autores": "Gabriel Henrique Neto, Helena Moraes Campos, Ivan Rodrigues Lima"
    },
    54: {
        "titulo": "Participação Política Juvenil e Democracia Digital no Brasil",
        "descricao": (
            "A relação entre juventude, participação política e democracia tem sido reconfigurada "
            "pelas possibilidades abertas pelas tecnologias digitais de comunicação e mobilização. "
            "Este projeto investiga as formas de engajamento político de jovens brasileiros de "
            "18 a 29 anos nas redes digitais e nas instâncias de participação institucional, "
            "analisando como as práticas digitais se articulam ou se contrapõem aos mecanismos "
            "tradicionais de representação política. A pesquisa combina survey online com amostra "
            "de 1.200 jovens de diferentes regiões e perfis socioeconômicos, grupos focais e "
            "análise de conteúdo de perfis e grupos políticos em redes sociais. "
            "Os resultados contribuirão para a compreensão das transformações contemporâneas "
            "da cultura política juvenil e para o debate sobre o fortalecimento da democracia "
            "participativa em contextos de crescente digitalização da esfera pública."
        ),
        "lattes_id": "7362904817736290",
        "autores": "Joana Cristina Abreu, Kelvin Augusto Rocha, Lídia Fernandes Prado"
    },
    55: {
        "titulo": "Precarização do Trabalho e Desemprego Estrutural na Era da Plataformização",
        "descricao": (
            "A expansão das plataformas digitais de trabalho — como aplicativos de transporte, "
            "entrega e serviços domésticos — tem promovido novas formas de precarização laboral "
            "que desafiam as categorias tradicionais do direito do trabalho e da proteção social. "
            "Este projeto analisa as condições de trabalho, renda e proteção social de "
            "trabalhadores de plataformas em cinco capitais brasileiras, investigando as "
            "percepções dos trabalhadores sobre autonomia, controle algorítmico e solidariedade "
            "coletiva. A metodologia inclui survey com 800 trabalhadores de plataformas, "
            "entrevistas em profundidade e análise documental de contratos e termos de uso "
            "das principais plataformas. Os resultados subsidiarão propostas de regulação "
            "do trabalho em plataformas compatíveis com os padrões de proteção social "
            "previstos na Consolidação das Leis do Trabalho e na Constituição Federal."
        ),
        "lattes_id": "1829473650182947",
        "autores": "Marcos Vinícius Leal, Nadine Cristina Rezende, Osmar Luiz Barros"
    },
    56: {
        "titulo": "Neopentecostalismo, Política e Esfera Pública no Brasil Contemporâneo",
        "descricao": (
            "O crescimento do neopentecostalismo nas últimas décadas transformou profundamente "
            "o campo religioso brasileiro e suas interfaces com a política. Este projeto investiga "
            "as estratégias de inserção das igrejas neopentecostais na esfera pública e no campo "
            "político, analisando a articulação entre discurso religioso, mobilização eleitoral "
            "e formulação de políticas públicas em temas como educação, família e segurança. "
            "A pesquisa realiza etnografia em três grandes igrejas neopentecostais do Rio de "
            "Janeiro e São Paulo, análise do discurso de líderes religiosos em mídias sociais "
            "e estudo das bancadas evangélicas no Congresso Nacional. "
            "Os resultados contribuem para compreender as transformações do laicismo estatal "
            "e as novas configurações entre religião, política e democracia no Brasil."
        ),
        "lattes_id": "4738201956473820",
        "autores": "Patrícia Gomes Alves, Quirino Batista Farias, Rebeca Andrade Melo"
    },
    57: {
        "titulo": "Encarceramento em Massa e Política Penal no Brasil Pós-1988",
        "descricao": (
            "O Brasil possui a terceira maior população carcerária do mundo, com mais de 830 mil "
            "pessoas privadas de liberdade em um sistema com capacidade para menos de 500 mil. "
            "Este projeto analisa os determinantes políticos, jurídicos e sociais do crescimento "
            "do encarceramento no Brasil entre 1988 e 2023, investigando as mudanças legislativas, "
            "as práticas policiais e judiciárias e os discursos sobre segurança pública que "
            "sustentam a expansão punitiva. A pesquisa combina análise de dados estatísticos "
            "do sistema prisional, análise legislativa e entrevistas com operadores do sistema "
            "de justiça criminal, gestores prisionais e pessoas em situação de privação de "
            "liberdade. Os resultados contribuirão para o debate sobre alternativas ao "
            "encarceramento e para a formulação de uma política penal compatível com os "
            "princípios constitucionais da dignidade humana e da ressocialização."
        ),
        "lattes_id": "7093847261709384",
        "autores": "Samuel Ferreira Coelho, Taísa Melo Gonçalves, Ulrico Pinheiro Ramos"
    },
    58: {
        "titulo": "Políticas de Ações Afirmativas para Mulheres no Mercado de Trabalho",
        "descricao": (
            "As desigualdades de gênero no mercado de trabalho brasileiro persistem apesar dos "
            "avanços legislativos e das políticas de igualdade das últimas décadas. Este projeto "
            "avalia o impacto de políticas de ações afirmativas implementadas por grandes "
            "empresas e organizações públicas — cotas para contratação, programas de mentoría "
            "e metas de promoção — sobre a inserção e progressão das mulheres em cargos de "
            "liderança. A pesquisa adota desenho quasi-experimental, comparando indicadores "
            "de representação feminina em organizações com e sem políticas afirmativas ao "
            "longo de 10 anos (2013-2023). Entrevistas com gestoras beneficiadas e não "
            "beneficiadas exploram as percepções sobre barreiras, oportunidades e o papel "
            "das políticas afirmativas nas trajetórias profissionais. Os resultados subsidiarão "
            "a elaboração de diretrizes nacionais de equidade de gênero no trabalho."
        ),
        "lattes_id": "3284710952328471",
        "autores": "Vera Lúcia Torres, Wilson Siqueira Nunes, Xênia Rocha Ferreira"
    },
    59: {
        "titulo": "Integração Regional e Diplomacia no Mercosul: Desafios Contemporâneos",
        "descricao": (
            "O Mercosul atravessa um período de tensões e redefinições no contexto das transformações "
            "da ordem internacional e das mudanças políticas internas nos países membros. "
            "Este projeto analisa os processos de integração regional no âmbito do Mercosul, "
            "investigando os avanços e retrocessos na harmonização de políticas comerciais, "
            "sociais e ambientais entre Argentina, Brasil, Paraguai e Uruguai no período 2010-2023. "
            "A pesquisa combina análise documental de tratados, protocolos e atas das cúpulas "
            "presidenciais, entrevistas com diplomatas e negociadores, e análise comparada "
            "de indicadores de integração econômica e social. Os resultados contribuirão "
            "para o debate acadêmico e diplomático sobre o futuro do regionalismo sul-americano "
            "e as perspectivas de aprofundamento da integração no contexto multipolar."
        ),
        "lattes_id": "6019384725601938",
        "autores": "Yolanda Batista Cruz, Zeno Marcos Prado, Aída Fernandes Borges"
    },
    60: {
        "titulo": "Movimentos Sociais Rurais e Reforma Agrária no Brasil: MST e Territórios",
        "descricao": (
            "O Movimento dos Trabalhadores Rurais Sem Terra (MST) constitui um dos movimentos "
            "sociais mais significativos da história recente do Brasil, com atuação em 24 estados "
            "e envolvimento de centenas de milhares de famílias em acampamentos e assentamentos. "
            "Este projeto analisa as transformações nas estratégias de luta e nos modelos "
            "produtivos do MST entre 2003 e 2023, investigando como o movimento articula "
            "a demanda por terra com questões de agroecologia, soberania alimentar e "
            "desenvolvimento territorial. A pesquisa realiza estudo de caso em quatro "
            "assentamentos de reforma agrária no Paraná e no Rio Grande do Sul, com "
            "observação participante, entrevistas com assentados e lideranças, e análise "
            "de projetos de desenvolvimento territorial. Os resultados contribuirão para "
            "a compreensão das perspectivas contemporâneas da reforma agrária e do "
            "desenvolvimento rural sustentável no Brasil."
        ),
        "lattes_id": "9284750163928475",
        "autores": "Benedito Luiz Alves, Célia Cristina Moreira, Daniel Rodrigues Assis"
    },

    # ---- BLOCO 7: IDs 61-70 (Engenharia) ----------------------------------
    61: {
        "titulo": "Durabilidade do Concreto em Estruturas de Pontes Submetidas a Cloretos",
        "descricao": (
            "A deterioração prematura de estruturas de concreto armado em pontes e viadutos "
            "representa um grave problema de engenharia e segurança pública no Brasil. "
            "A penetração de íons cloreto, provenientes da névoa marinha em regiões costeiras "
            "ou de sais de degelo em regiões frias, é a principal causa de corrosão das "
            "armaduras e colapso das estruturas. Este projeto avalia a durabilidade de "
            "concretos com diferentes adições minerais (sílica ativa, metacaulim e cinza "
            "volante) frente à penetração de cloretos em condições de imersão e névoa "
            "salina acelerada. Serão determinados coeficientes de difusão de cloretos, "
            "profundidade de carbonatação e resistência à compressão ao longo de 18 meses. "
            "Modelos de vida útil serão calibrados com os dados experimentais para prever "
            "o tempo de iniciação da corrosão em diferentes condições de exposição, "
            "subsidiar projetos de estruturas em zonas agressivas e orientar programas "
            "de manutenção preventiva."
        ),
        "lattes_id": "2847196503284719",
        "autores": "Estevão Menezes Santos, Flávia Cristina Borges, Gilberto Luiz Ramos"
    },
    62: {
        "titulo": "Sistemas Fotovoltaicos Integrados à Edificação: Eficiência e Geração Distribuída",
        "descricao": (
            "A geração distribuída de energia solar fotovoltaica tem crescido exponencialmente "
            "no Brasil, impulsionada pela queda de custos dos painéis e pela regulamentação "
            "favorável da ANEEL. Este projeto avalia o desempenho de sistemas fotovoltaicos "
            "integrados a edificações (BIPV) em diferentes configurações de instalação "
            "(telhado inclinado, fachada vertical e cobertura horizontal) em clima tropical "
            "úmido de Manaus e clima semiárido de Petrolina. Serão monitorados por 24 meses "
            "a irradiância solar incidente, a potência gerada, a temperatura dos módulos "
            "e a eficiência de conversão em cada configuração. Os dados serão usados para "
            "validar modelos de simulação energética e para otimizar o dimensionamento "
            "de sistemas BIPV em diferentes climas brasileiros. O projeto inclui análise "
            "de viabilidade econômica considerando tarifas de energia, créditos de "
            "compensação e custo do ciclo de vida dos sistemas."
        ),
        "lattes_id": "5192847360519284",
        "autores": "Helena Aparecida Moura, Ilson Augusto Lima, Joelma Cristina Fonseca"
    },
    63: {
        "titulo": "Compósitos de Fibra de Carbono para Componentes Aeroespaciais Leves",
        "descricao": (
            "Os materiais compósitos de fibra de carbono com matriz polimérica (CFRP) são "
            "amplamente utilizados na indústria aeroespacial por sua elevada relação "
            "resistência/peso. Este projeto desenvolve e caracteriza laminados CFRP com "
            "diferentes sequências de empilhamento para aplicação em painéis de fuselagem "
            "e asas de aeronaves de pequeno porte. Corpos de prova serão fabricados por "
            "infusão a vácuo e autoclave, com variação de fração volumétrica de fibras "
            "e número de camadas. A caracterização mecânica inclui ensaios de tração, "
            "compressão, cisalhamento interlaminar e tenacidade à fratura em modo I e II. "
            "Modelos de elementos finitos serão desenvolvidos e validados com os dados "
            "experimentais para predizer o comportamento dos laminados sob cargas complexas. "
            "O projeto é desenvolvido em parceria com o Instituto Tecnológico de Aeronáutica "
            "e conta com apoio da indústria aeronáutica nacional."
        ),
        "lattes_id": "8374051928837405",
        "autores": "Kelton Rodrigues Melo, Lorena Batista Pinheiro, Maurício Henrique Costa"
    },
    64: {
        "titulo": "Otimização Logística em Cadeias de Suprimento com Lean Manufacturing",
        "descricao": (
            "A competitividade industrial brasileira depende crescentemente da eficiência "
            "das cadeias de suprimento e da adoção de práticas de manufatura enxuta. "
            "Este projeto desenvolve e aplica um framework de diagnóstico e otimização "
            "baseado nos princípios do lean manufacturing em 5 empresas do setor automotivo "
            "do ABC paulista, identificando e eliminando desperdícios nos fluxos de "
            "materiais e informação. A metodologia inclui mapeamento do fluxo de valor (VSM), "
            "análise de indicadores de desempenho (OEE, lead time, estoque em processo) "
            "e implementação de ferramentas como kanban, SMED e gestão visual. "
            "Os resultados das intervenções serão monitorados por 12 meses, com "
            "quantificação dos ganhos em produtividade, redução de estoques e lead time. "
            "Os casos estudados serão sistematizados como guia de boas práticas para "
            "a indústria de transformação brasileira."
        ),
        "lattes_id": "1847203956184720",
        "autores": "Núbia Cristina Farias, Osório Luiz Carvalho, Poliana Andrade Moreira"
    },
    65: {
        "titulo": "Biorreatores de Membrana para Tratamento de Efluentes Industriais",
        "descricao": (
            "O tratamento de efluentes industriais com alta carga orgânica e presença de "
            "compostos recalcitrantes é um desafio crescente para o setor industrial brasileiro, "
            "diante do aumento das exigências ambientais. Este projeto avalia o desempenho "
            "de biorreatores de membrana (MBR) com diferentes configurações de membrana "
            "(fibra oca de PVDF e membrana plana de polietileno) e diferentes condições "
            "operacionais (tempo de retenção hidráulica, tempo de retenção celular, "
            "aeração) no tratamento de efluente da indústria têxtil. Serão monitorados "
            "parâmetros de qualidade do efluente tratado (DQO, DBO, SST, turbidez, "
            "cor e micropoluentes emergentes) e parâmetros operacionais dos reatores "
            "(pressão transmembrana, colmatação, consumo energético). "
            "Um modelo matemático de desempenho do MBR será desenvolvido e validado "
            "para auxiliar no dimensionamento e operação de sistemas em escala real."
        ),
        "lattes_id": "4093817265409381",
        "autores": "Quezia Aparecida Gomes, Rivelino Prado Ferreira, Selma Cristina Barros"
    },
    66: {
        "titulo": "Saneamento Rural: Abastecimento de Água em Comunidades do Semiárido",
        "descricao": (
            "O acesso à água potável em quantidade e qualidade adequadas é um direito humano "
            "fundamental, ainda não plenamente garantido às populações rurais do semiárido "
            "nordestino. Este projeto avalia a qualidade da água fornecida por sistemas "
            "de abastecimento rural (cisternas, sistemas simplificados de abastecimento e "
            "carros-pipa) em 40 comunidades rurais de 5 municípios do sertão pernambucano, "
            "investigando a prevalência de parâmetros físico-químicos e microbiológicos "
            "fora dos padrões de potabilidade. A pesquisa inclui coleta e análise de amostras "
            "de água em pontos de captação, armazenamento e consumo, além de diagnóstico "
            "das condições de saneamento domiciliar. Com base nos resultados, serão "
            "propostas e avaliadas tecnologias de baixo custo para melhoria da qualidade "
            "da água nos domicílios, incluindo sistemas de desinfecção solar e filtros "
            "cerâmicos, com envolvimento das comunidades na gestão das soluções."
        ),
        "lattes_id": "7361904825736190",
        "autores": "Tadeu Marcos Rezende, Urânia Batista Melo, Vanderlei Luiz Cruz"
    },
    67: {
        "titulo": "Controle PID Adaptativo para Automação de Processos Industriais",
        "descricao": (
            "O controle de processos industriais por controladores PID (Proporcional-Integral-Derivativo) "
            "é amplamente utilizado na indústria química, petroquímica e de alimentos. "
            "A sintonia inadequada dos parâmetros do PID em processos com dinâmica variável "
            "resulta em oscilações, consumo energético excessivo e produto fora de especificação. "
            "Este projeto desenvolve e implementa um algoritmo de sintonia automática de "
            "controladores PID baseado em aprendizado por reforço, capaz de adaptar os "
            "parâmetros do controlador em tempo real às variações da dinâmica do processo. "
            "O algoritmo será testado em bancadas experimentais de controle de nível, "
            "temperatura e vazão, e comparado com métodos clássicos de sintonia "
            "(Ziegler-Nichols, IMC, CHR). A plataforma de implementação utilizará "
            "controladores lógicos programáveis (CLP) em ambiente industrial real, "
            "com interface SCADA para monitoramento e supervisão."
        ),
        "lattes_id": "3047281936304728",
        "autores": "Waldir Soares Nunes, Xandra Cristina Pires, Zacarias Henrique Lopes"
    },
    68: {
        "titulo": "Tribologia e Lubrificação de Superfícies em Componentes Mecânicos",
        "descricao": (
            "O desgaste tribológico de componentes mecânicos em contato deslizante representa "
            "uma das principais causas de falha em máquinas industriais, com impactos sobre "
            "produtividade e custos de manutenção. Este projeto investiga o comportamento "
            "tribológico de superfícies de aços ferramenta com diferentes tratamentos "
            "superficiais (nitretação a plasma, PVD e DLC) em contato com diferentes "
            "lubrificantes (convencional, biodegradável e nanofluido com partículas de "
            "óxido de grafeno). Ensaios de pino-sobre-disco e de quatro esferas serão "
            "realizados em tribômetro instrumentado com monitoramento in-situ por "
            "emissão acústica e temperatura. As superfícies de desgaste serão "
            "caracterizadas por microscopia eletrônica de varredura, espectroscopia "
            "Raman e perfilometria 3D. Os resultados orientarão a seleção de pares "
            "tribológicos e lubrificantes para aplicações industriais específicas, "
            "visando a extensão da vida útil de componentes mecânicos críticos."
        ),
        "lattes_id": "6193847250619384",
        "autores": "Abner Luiz Cavalcanti, Bianca Rocha Andrade, Clóvis Menezes Borges"
    },
    69: {
        "titulo": "Catálise Heterogênea em Processos Petroquímicos Verdes",
        "descricao": (
            "A indústria petroquímica busca alternativas mais sustentáveis aos catalisadores "
            "tradicionais baseados em metais nobres e ácidos minerais. Este projeto sintetiza "
            "e caracteriza catalisadores heterogêneos baseados em óxidos mistos de metais "
            "de transição (Fe-Mo, Ni-Co, Mn-Ce) para reações de desidratação, esterificação "
            "e reforma a vapor de biomassa lignocelulósica. Os catalisadores serão "
            "preparados por co-precipitação, sol-gel e impregnação úmida, e caracterizados "
            "por difração de raios-X, fisissorção de N2, microscopia eletrônica de "
            "transmissão e espectroscopia UV-Vis. Os testes catalíticos serão realizados "
            "em reator de leito fixo, avaliando atividade, seletividade e estabilidade "
            "dos catalisadores em função da temperatura, pressão e composição da alimentação. "
            "Os catalisadores mais promissores serão avaliados em escala piloto em "
            "parceria com unidade industrial do setor de biocombustíveis."
        ),
        "lattes_id": "9284726038928472",
        "autores": "Danilo Cristiano Fonseca, Elis Ferreira Guimarães, Francisco Luiz Assis"
    },
    70: {
        "titulo": "Estabilidade de Taludes em Encostas Urbanas: Análise de Risco e Monitoramento",
        "descricao": (
            "Os deslizamentos em encostas urbanas são um dos desastres naturais de maior "
            "impacto humano no Brasil, com centenas de mortes registradas anualmente "
            "em cidades serranas e litorâneas. Este projeto avalia a estabilidade de "
            "taludes em áreas de ocupação urbana irregular em Nova Friburgo (RJ), "
            "combinando levantamentos geotécnicos de campo, ensaios de laboratório "
            "e modelos de análise de estabilidade. Serão instalados instrumentos "
            "de monitoramento automático (piezômetros, inclinômetros e extensômetros) "
            "em taludes críticos identificados em estudo de risco geológico. "
            "Um sistema de alerta antecipado baseado em limites de chuva e "
            "deslocamento será desenvolvido e integrado ao sistema municipal "
            "de proteção e defesa civil. Os resultados contribuirão para o "
            "aprimoramento dos critérios de análise de risco geotécnico e para "
            "a definição de intervenções prioritárias de estabilização em áreas "
            "de alto risco."
        ),
        "lattes_id": "2047381956204738",
        "autores": "Genival Rodrigues Prado, Hortência Cristina Lima, Isaías Batista Neto"
    },

    # ---- BLOCO 8: IDs 71-80 (Letras) --------------------------------------
    71: {
        "titulo": "Literatura Afro-Brasileira Contemporânea: Identidade, Memória e Resistência",
        "descricao": (
            "A literatura afro-brasileira contemporânea tem se consolidado como campo "
            "de grande vitalidade criativa e relevância política, com autoras e autores "
            "como Conceição Evaristo, Itamar Vieira Jr. e Jeferson Tenório ganhando "
            "crescente reconhecimento nacional e internacional. Este projeto analisa "
            "as representações de identidade racial, memória da escravidão e resistência "
            "cotidiana em romances e contos publicados entre 2010 e 2023 por escritoras "
            "e escritores negros brasileiros. A pesquisa emprega metodologia de crítica "
            "literária interseccional, articulando raça, gênero e classe na análise "
            "das narrativas. Serão produzidas análises individuais de obras selecionadas "
            "e estudos comparativos entre diferentes autores e contextos regionais. "
            "O projeto inclui atividades de extensão com mediação de leitura em escolas "
            "públicas de Campinas, buscando ampliar o acesso à literatura afro-brasileira "
            "entre estudantes do ensino fundamental e médio."
        ),
        "lattes_id": "5193820746519382",
        "autores": "Jacira Moraes Cunha, Ladislau Ferreira Mota, Mirela Batista Rocha"
    },
    72: {
        "titulo": "Ensino de Língua Estrangeira e Interculturalidade em Contextos Escolares",
        "descricao": (
            "O ensino de língua estrangeira na educação básica brasileira deve contemplar "
            "não apenas o desenvolvimento da competência linguística, mas também a "
            "formação intercultural dos estudantes, preparando-os para o diálogo "
            "com outras culturas de forma crítica e respeitosa. Este projeto investiga "
            "práticas pedagógicas interculturais no ensino de espanhol e inglês "
            "em 8 escolas públicas estaduais de São Paulo, analisando como professores "
            "integram elementos culturais às aulas de língua e como os estudantes "
            "constroem sua identidade linguístico-cultural nesse processo. "
            "A metodologia inclui observação de aulas, entrevistas com professores "
            "e grupos focais com estudantes. Os resultados subsidiarão a elaboração "
            "de sequências didáticas interculturais para o ensino de línguas estrangeiras "
            "na educação básica, disponibilizadas em repositório aberto para professores "
            "da rede pública."
        ),
        "lattes_id": "8374610293837461",
        "autores": "Nelson Augusto Farias, Oriana Cristina Lemos, Priscila Barros Andrade"
    },
    73: {
        "titulo": "Tradução e Adaptação Cultural de Literatura Infantil para o Contexto Brasileiro",
        "descricao": (
            "A tradução de literatura infantil envolve não apenas a transposição linguística, "
            "mas também complexas negociações culturais que determinam o que é considerado "
            "apropriado, pedagogicamente adequado e esteticamente apreciável para crianças "
            "em diferentes contextos. Este projeto analisa as estratégias de tradução e "
            "adaptação cultural empregadas em 50 obras de literatura infantil traduzidas "
            "para o português brasileiro nos últimos 20 anos, com foco em álbuns ilustrados "
            "provenientes de culturas anglófonas, francófonas e japonesas. A análise "
            "examina as escolhas lexicais, as adaptações de referências culturais, "
            "as modificações de elementos visuais e as estratégias de domesticação "
            "e estrangeirização adotadas pelos tradutores. Os resultados contribuirão "
            "para a formação de tradutores especializados em literatura infantil e "
            "para o debate sobre ética e política de tradução para crianças."
        ),
        "lattes_id": "1948273650194827",
        "autores": "Querino Batista Campos, Rosane Cristina Torres, Silvério Luiz Moreira"
    },
    74: {
        "titulo": "Análise do Discurso Político Midiático em Eleições Presidenciais",
        "descricao": (
            "As eleições presidenciais de 2018 e 2022 no Brasil foram marcadas pela intensa "
            "presença das mídias digitais e pela circulação massiva de desinformação. "
            "Este projeto analisa, por meio de análise do discurso de orientação francesa "
            "(AD), os mecanismos de construção das representações dos candidatos e "
            "das posições políticas em matérias de jornal, programas eleitorais e "
            "posts em redes sociais nos dois pleitos. Serão analisados corpora paralelos "
            "em diferentes suportes midiáticos, investigando os processos de "
            "interdiscursividade, formações discursivas e efeitos de sentido. "
            "Particular atenção será dada à circulação de discursos de ódio e à "
            "construção discursiva dos outros políticos como inimigos. "
            "Os resultados contribuirão para a compreensão crítica da linguagem "
            "política contemporânea e para a formação de leitores críticos das mídias."
        ),
        "lattes_id": "4730192856473019",
        "autores": "Telma Aparecida Ramos, Ulisses Rodrigues Vieira, Vitória Helena Mendes"
    },
    75: {
        "titulo": "Modernismo Brasileiro: Drummond, Bandeira e a Poética da Memória",
        "descricao": (
            "Carlos Drummond de Andrade e Manuel Bandeira são duas das vozes mais representativas "
            "da poesia modernista brasileira, e a memória — pessoal, histórica e cultural — "
            "constitui um dos temas centrais de suas obras. Este projeto realiza uma leitura "
            "comparatista da poética da memória nos dois autores, investigando como constroem "
            "literariamente o passado, a infância e os lugares de origem em contraposição "
            "à experiência urbana moderna. A análise privilegia aspectos formais "
            "(verso, metro, ritmo, imagem) articulados às dimensões semânticas e "
            "intertextuais dos poemas selecionados. O corpus abrange tanto poemas "
            "canônicos quanto textos menos estudados dos dois autores, disponíveis "
            "em edições críticas. Os resultados serão publicados em artigos e capítulos "
            "de livro, contribuindo para a historiografia literária do modernismo brasileiro."
        ),
        "lattes_id": "7193847052719384",
        "autores": "Wanderley Cristiano Borges, Ximena Aparecida Fonseca, Yanna Rodrigues Lima"
    },
    76: {
        "titulo": "Variação Dialetal no Português Nordestino: Corpus e Análise Sociolinguística",
        "descricao": (
            "O português falado no Nordeste do Brasil apresenta variação dialetal de grande "
            "interesse linguístico, com traços fonéticos, morfossintáticos e lexicais que "
            "o diferenciam das variedades centro-sulinas e que são frequentemente "
            "estigmatizados nos contextos de mobilidade e comunicação nacional. "
            "Este projeto documenta e analisa a variação dialetal no português "
            "falado em comunidades rurais e urbanas de quatro estados nordestinos "
            "(Bahia, Ceará, Pernambuco e Maranhão), constituindo um corpus oral "
            "de 400 horas de gravação. As variáveis linguísticas investigadas incluem "
            "a realização do /r/ em coda silábica, a concordância verbal e nominal "
            "e o uso de formas pronominais. A análise sociolinguística correlaciona "
            "a variação com fatores como faixa etária, escolaridade, gênero e "
            "mobilidade geográfica, contribuindo para o mapeamento da diversidade "
            "linguística do português brasileiro."
        ),
        "lattes_id": "3048190265304819",
        "autores": "Zilda Cristina Assis, Afonso Luiz Gonçalves, Belarmino Ferreira Cruz"
    },
    77: {
        "titulo": "Intertextualidade e Mito na Obra de José Saramago",
        "descricao": (
            "José Saramago é um dos mais importantes escritores de língua portuguesa do "
            "século XX, com uma obra caracterizada pelo diálogo constante com a tradição "
            "literária e mitológica ocidental. Este projeto analisa os procedimentos "
            "intertextuais e a reelaboração de mitos clássicos em romances selecionados "
            "do autor: O Evangelho Segundo Jesus Cristo, Ensaio sobre a Cegueira e "
            "As Intermitências da Morte. A pesquisa examina como Saramago subverte "
            "e ressignifica narrativas míticas e religiosas para realizar uma crítica "
            "social e política do presente. O referencial teórico articula as teorias "
            "da intertextualidade (Kristeva, Genette) com abordagens da literatura "
            "comparada e estudos culturais. Os resultados contribuirão para o "
            "entendimento da singularidade estética e do projeto crítico da ficção "
            "saramaguiana no contexto da literatura portuguesa e mundial."
        ),
        "lattes_id": "6284731059628473",
        "autores": "Cedenir Batista Melo, Dionísia Aparecida Nunes, Evelize Rocha Pinto"
    },
    78: {
        "titulo": "Terminologia Científica em Português Brasileiro: Lexicografia Especializada",
        "descricao": (
            "A produção e difusão do conhecimento científico em português brasileiro demandam "
            "o desenvolvimento de recursos terminológicos atualizados nas diferentes áreas "
            "do saber. Este projeto elabora um dicionário terminológico bilíngue "
            "(português-inglês) da área de bioinformática, contemplando aproximadamente "
            "2.000 termos especializados de uso frequente em artigos científicos e "
            "na comunicação entre especialistas. O projeto adota a metodologia da "
            "Teoria Comunicativa da Terminologia (TCT) e da Terminologia Baseada em Corpus, "
            "extraindo e validando os termos a partir de um corpus especializado de "
            "100 milhões de palavras. Cada verbete contém definição em português, "
            "equivalente em inglês, contexto de uso, informações gramaticais e "
            "remissivas a termos relacionados. O dicionário será disponibilizado "
            "em formato digital de acesso livre, em plataforma que permitirá "
            "atualizações colaborativas pela comunidade especializada."
        ),
        "lattes_id": "9371820465937182",
        "autores": "Florêncio Rodrigues Barros, Gracinda Cristina Souza, Hilton Luiz Fonseca"
    },
    79: {
        "titulo": "Metáforas Conceptuais no Português Brasileiro: Uma Abordagem Cognitiva",
        "descricao": (
            "A teoria da metáfora conceptual, desenvolvida por Lakoff e Johnson, propõe que "
            "as metáforas não são apenas figuras de linguagem, mas estruturas conceptuais "
            "que organizam o pensamento e a ação humana. Este projeto investiga metáforas "
            "conceptuais recorrentes no português brasileiro em três domínios discursivos: "
            "o político, o econômico e o das doenças infecciosas. A pesquisa constrói "
            "corpora de textos jornalísticos, parlamentares e médico-populares de "
            "diferentes períodos (2010-2023) e aplica metodologia de análise metafórica "
            "baseada em corpus (CADS). São investigadas as metáforas estruturais, "
            "orientacionais e ontológicas predominantes em cada domínio, e como "
            "sua frequência e tipos variam ao longo do tempo e entre diferentes "
            "veículos de comunicação. Os resultados contribuem para a linguística "
            "cognitiva do português e para a análise crítica dos discursos "
            "públicos no Brasil."
        ),
        "lattes_id": "2048371956204837",
        "autores": "Irene Batista Ferreira, Júlio Augusto Menezes, Kézia Cristina Andrade"
    },
    80: {
        "titulo": "Letramento Funcional de Adultos na EJA: Práticas de Leitura e Escrita",
        "descricao": (
            "A Educação de Jovens e Adultos (EJA) atende uma parcela significativa da "
            "população brasileira que não concluiu a educação básica na idade regular, "
            "frequentemente marcada por trajetórias de exclusão social e escolar. "
            "Este projeto investiga as práticas de letramento de estudantes da EJA "
            "em duas escolas municipais de Salvador, analisando como os sujeitos "
            "utilizam a leitura e a escrita em seus contextos cotidianos (trabalho, "
            "família, comunidade) e como essas práticas se articulam com as exigidas "
            "pela escola. A pesquisa adota perspectiva etnográfica, com observação "
            "participante, entrevistas narrativas e análise de artefatos textuais "
            "produzidos pelos estudantes. Os resultados contribuirão para a "
            "elaboração de práticas pedagógicas de letramento mais contextualizadas "
            "e significativas para os estudantes da EJA, fundamentadas em seus "
            "repertórios culturais e necessidades concretas de uso da linguagem."
        ),
        "lattes_id": "5193827046519382",
        "autores": "Leonida Rodrigues Prado, Manoel Cristiano Torres, Norma Aparecida Guimarães"
    },

    # ---- BLOCO 9: IDs 81-90 (Ciências Exatas) ----------------------------
    81: {
        "titulo": "Síntese e Avaliação Biológica de Compostos Orgânicos com Atividade Antimicrobiana",
        "descricao": (
            "A resistência bacteriana a antibióticos convencionais impulsiona a busca por "
            "novos compostos bioativos com mecanismos de ação inovadores. Este projeto "
            "sintetiza e avalia a atividade antimicrobiana de uma série de compostos "
            "orgânicos derivados de chalconas, cumarinas e quinolonas, obtidos por "
            "reações de condensação aldólica e ciclocondensação a partir de precursores "
            "de baixo custo. Os compostos serão purificados por cromatografia em coluna "
            "e caracterizados por RMN ¹H e ¹³C, espectrometria de massas e análise "
            "elementar. A atividade antimicrobiana será avaliada frente a cepas "
            "padrão ATCC e cepas resistentes de Staphylococcus aureus, Escherichia "
            "coli, Pseudomonas aeruginosa e Candida albicans, determinando a "
            "concentração inibitória mínima (CIM) e a concentração bactericida "
            "mínima (CBM). A citotoxicidade dos compostos ativos será avaliada "
            "em linhagens celulares humanas normais."
        ),
        "lattes_id": "8274039165827403",
        "autores": "Olívia Batista Farias, Paulino Rodrigues Melo, Quitéria Aparecida Braga"
    },
    82: {
        "titulo": "Propriedades Quânticas de Nanomateriais Semicondutores: Teoria e Experimento",
        "descricao": (
            "Os nanomateriais semicondutores (pontos quânticos, nanofios e nanoplacas) "
            "apresentam propriedades eletrônicas e ópticas únicas decorrentes do "
            "confinamento quântico, com aplicações em LEDs, células solares e "
            "sensores biológicos. Este projeto investiga as propriedades quânticas "
            "de pontos quânticos de CdSe/ZnS e nanoplaquetas de CdSe, combinando "
            "cálculos de primeiros princípios (DFT e GW/BSE) com caracterização "
            "experimental por espectroscopia de absorção e emissão, tempo de vida "
            "de fluorescência e microscopia de transmissão de alta resolução. "
            "Será investigada a influência do tamanho, forma e composição da casca "
            "sobre o gap de energia, a eficiência quântica e a estabilidade "
            "fotoquímica dos nanomateriais. Os resultados contribuirão para o "
            "design racional de nanomateriais com propriedades ópticas otimizadas "
            "para aplicações em optoeletrônica e fotônica."
        ),
        "lattes_id": "1948372560194837",
        "autores": "Raimundo Luiz Cavalcanti, Sara Cristina Lopes, Tércio Henrique Borges"
    },
    83: {
        "titulo": "Modelagem Matemática de Doenças Infecciosas com Equações Diferenciais",
        "descricao": (
            "A modelagem matemática de epidemias tem papel central na compreensão da dinâmica "
            "de transmissão de doenças infecciosas e no planejamento de estratégias de "
            "controle e prevenção. Este projeto desenvolve e analisa modelos compartimentais "
            "baseados em equações diferenciais ordinárias e parciais para descrever a "
            "dinâmica de transmissão de dengue, COVID-19 e influenza no Brasil, "
            "incorporando heterogeneidades populacionais (faixa etária, estrutura espacial "
            "e vacinação) e a influência de fatores climáticos sobre os parâmetros "
            "de transmissão. Os modelos serão calibrados com dados epidemiológicos "
            "reais do DATASUS e da FIOCRUZ. Análise de sensibilidade e incerteza "
            "dos parâmetros permitirá identificar as intervenções de maior impacto. "
            "Os modelos desenvolvidos serão disponibilizados como ferramentas de "
            "apoio à tomada de decisão para gestores de saúde pública."
        ),
        "lattes_id": "4731028956473102",
        "autores": "Udenilson Aparecido Costa, Vanda Rodrigues Nunes, Waldir Cristiano Lima"
    },
    84: {
        "titulo": "Análise Multivariada de Dados Socioeconômicos: Modelos e Aplicações",
        "descricao": (
            "O desenvolvimento de modelos estatísticos multivariados para análise de dados "
            "socioeconômicos de grande dimensão apresenta desafios metodológicos importantes, "
            "especialmente quando os dados exibem estrutura de painel, dependência espacial "
            "e distribuições não-gaussianas. Este projeto desenvolve e aplica métodos de "
            "análise multivariada — incluindo modelos de equações estruturais, análise "
            "de componentes principais esparsa e modelos mistos generalizados — a bases "
            "de dados das PNADs Contínuas e do Censo Demográfico para investigar "
            "os determinantes das desigualdades de renda, educação e saúde no Brasil. "
            "Particular atenção será dada ao desenvolvimento de estimadores robustos "
            "para dados com valores ausentes e outliers. Os métodos desenvolvidos "
            "serão implementados em pacotes de software de código aberto para R "
            "e Python, disponibilizados para pesquisadores e analistas de políticas públicas."
        ),
        "lattes_id": "7283940165728394",
        "autores": "Xilene Batista Assis, Ytalo Rodrigues Ferreira, Zaíra Cristina Mota"
    },
    85: {
        "titulo": "Espectrometria de Massas para Detecção de Contaminantes Emergentes em Água",
        "descricao": (
            "Os contaminantes emergentes — fármacos, hormônios, pesticidas e produtos de "
            "higiene pessoal — são encontrados em concentrações traço em corpos d'água "
            "e representam riscos ainda pouco compreendidos para a biota aquática e "
            "a saúde humana. Este projeto desenvolve e valida métodos analíticos "
            "baseados em cromatografia líquida acoplada à espectrometria de massas "
            "de alta resolução (LC-HRMS) para a determinação simultânea de 80 "
            "contaminantes emergentes em amostras de água superficial, subterrânea "
            "e de abastecimento público. Os métodos desenvolvidos serão aplicados "
            "ao monitoramento de 10 estações de tratamento de água e efluentes "
            "no estado de São Paulo, com coletas sazonais ao longo de 2 anos. "
            "A presença e persistência dos contaminantes ao longo dos processos "
            "de tratamento convencional serão avaliadas, subsidiando a adoção "
            "de tratamentos avançados quando necessário."
        ),
        "lattes_id": "3019847265301984",
        "autores": "Adair Luiz Gonçalves, Benedita Aparecida Cruz, Celso Rodrigues Barros"
    },
    86: {
        "titulo": "Materiais Magnéticos Nanoestruturados: Síntese, Propriedades e Aplicações",
        "descricao": (
            "Os materiais magnéticos nanoestruturados têm aplicações promissoras em "
            "armazenamento de dados, hipertermia magnética para tratamento de câncer "
            "e catálise ambiental. Este projeto sintetiza e caracteriza nanopartículas "
            "de óxido de ferro (magnetita, maguemita e hematita) e ferrites de Co, "
            "Ni e Mn por co-precipitação, decomposição térmica e método solvotermal, "
            "investigando a influência das condições de síntese sobre o tamanho, "
            "forma, cristalinidade e propriedades magnéticas. Os materiais serão "
            "caracterizados por difratometria de raios-X, microscopia eletrônica "
            "de transmissão, espectroscopia Mössbauer, magnetometria de amostra "
            "vibrante (VSM) e medidas de susceptibilidade AC. Serão avaliadas "
            "aplicações em remoção de metais pesados de efluentes e como "
            "agentes de contraste para imagem por ressonância magnética (MRI)."
        ),
        "lattes_id": "6184739025618473",
        "autores": "Dalva Cristina Fonseca, Edmilson Batista Rocha, Felicidade Rodrigues Melo"
    },
    87: {
        "titulo": "Teoria dos Grupos Finitos: Estrutura, Representações e Aplicações",
        "descricao": (
            "A teoria dos grupos finitos é um ramo fundamental da álgebra abstrata, com "
            "conexões profundas com a teoria dos números, a geometria algébrica e a "
            "física matemática. Este projeto investiga a estrutura de grupos finitos "
            "solúveis e não-solúveis com restrições sobre seus subgrupos, estendendo "
            "resultados clássicos de Sylow e Hall. São estudadas representações de "
            "grupos finitos sobre corpos de característica prima e suas aplicações "
            "à teoria dos caracteres modulares e à teoria de blocos de Brauer. "
            "O projeto também explora conexões com a topologia algébrica por meio "
            "de cohomologia de grupos. As demonstrações serão formalizadas "
            "utilizando o assistente de prova Lean 4, contribuindo para o "
            "desenvolvimento da biblioteca de matemática formalizada Mathlib. "
            "Os resultados serão publicados em periódicos especializados de "
            "álgebra e combinatória."
        ),
        "lattes_id": "9273846015927384",
        "autores": "Genésio Luiz Andrade, Hêlena Aparecida Pires, Ildemar Rodrigues Borges"
    },
    88: {
        "titulo": "Fotocatálise Heterogênea para Degradação de Pesticidas em Solo Agrícola",
        "descricao": (
            "O uso intensivo de pesticidas na agricultura brasileira resulta na contaminação "
            "de solos e lençóis freáticos, com riscos à saúde humana e à biodiversidade. "
            "Este projeto avalia a eficácia de processos fotocatalíticos avançados "
            "baseados em TiO2 dopado com metais de transição (Fe, Cu, N) para a "
            "degradação de pesticidas organofosforados (glifosato, clorpirifós) e "
            "triazinas (atrazina, simazina) em amostras de solo e solução aquosa. "
            "Os fotocatalisadores serão sintetizados pelo método sol-gel e "
            "caracterizados por DRX, BET, UV-Vis e microscopia eletrônica. "
            "Os experimentos de fotocatálise serão realizados em reatores com "
            "iluminação UV e solar simulada, monitorando a degradação dos "
            "pesticidas por HPLC-MS e a mineralização por TOC. "
            "A ecotoxicidade dos produtos de degradação será avaliada com "
            "bioensaios com Daphnia magna e sementes de alface."
        ),
        "lattes_id": "2047381956204738",
        "autores": "Joelma Batista Carvalho, Kátila Rodrigues Vieira, Leomar Aparecido Neto"
    },
    89: {
        "titulo": "Inferência Bayesiana em Modelos Hierárquicos para Dados de Saúde",
        "descricao": (
            "Os modelos hierárquicos bayesianos oferecem uma estrutura flexível para análise "
            "de dados com estrutura multinível — como pacientes aninhados em hospitais, "
            "municípios e estados — amplamente presentes nos sistemas de informação em saúde. "
            "Este projeto desenvolve e aplica modelos bayesianos hierárquicos para análise "
            "de dados de mortalidade infantil, internações por doenças crônicas e cobertura "
            "vacinal nos municípios brasileiros, utilizando os bancos do SIM, SIH e SI-PNI. "
            "Os modelos incorporam covariáveis socioeconômicas e de infraestrutura de saúde "
            "e permitem a estimação de efeitos aleatórios municipais para identificação de "
            "outliers positivos e negativos de desempenho dos sistemas locais de saúde. "
            "A inferência será conduzida via MCMC com Stan e INLA, e os resultados "
            "serão apresentados como mapas de risco relativo com incerteza quantificada."
        ),
        "lattes_id": "5193827046051938",
        "autores": "Marlene Cristina Assis, Nonato Rodrigues Lima, Olindina Batista Fonseca"
    },
    90: {
        "titulo": "Simulação Computacional de Escoamentos Turbulentos em Geometrias Complexas",
        "descricao": (
            "A simulação numérica de escoamentos turbulentos em geometrias complexas é "
            "fundamental para o projeto de sistemas de ventilação, turbinas eólicas "
            "e aeronaves. Este projeto desenvolve e valida metodologias de simulação "
            "de dinâmica dos fluidos computacional (CFD) para escoamentos turbulentos "
            "internos e externos em geometrias tridimensionais complexas, utilizando "
            "as abordagens RANS, LES e DNS em código de volumes finitos de alta ordem. "
            "Os resultados das simulações são validados com dados experimentais "
            "obtidos por velocimetria por imagem de partículas (PIV) e anemometria "
            "de fio quente em bancadas instrumentadas do laboratório. "
            "Particular atenção é dada ao desenvolvimento de modelos de turbulência "
            "adaptados para escoamentos com separação de camada limite e instabilidades "
            "de Kelvin-Helmholtz. Os métodos serão disponibilizados como extensões "
            "do solver OpenFOAM de código aberto."
        ),
        "lattes_id": "8374016925837401",
        "autores": "Patrocínio Luiz Borges, Querina Aparecida Melo, Remigio Rodrigues Prado"
    },

    # ---- BLOCO 10: IDs 91-100 (Ciências Ambientais) ----------------------
    91: {
        "titulo": "Modelagem de Emissões de GEE e Cenários de Mitigação para o Agronegócio",
        "descricao": (
            "O setor agropecuário brasileiro responde por aproximadamente 27% das emissões "
            "nacionais de gases de efeito estufa (GEE), principalmente pelo desmatamento, "
            "pela pecuária bovina e pelo cultivo de arroz irrigado. Este projeto quantifica "
            "e modela as emissões de CO2, CH4 e N2O provenientes de sistemas de produção "
            "agropecuária no Mato Grosso e no Pará, utilizando dados de inventário de campo "
            "e sensoriamento remoto. São construídos cenários de mitigação baseados na "
            "adoção do Plano ABC (Agricultura de Baixo Carbono) e estimados os potenciais "
            "de redução de emissões associados ao plantio direto, à integração "
            "lavoura-pecuária-floresta e ao tratamento de dejetos animais. "
            "Um modelo econométrico avalia os fatores que determinam a adoção "
            "dessas tecnologias pelos produtores, considerando incentivos "
            "econômicos, crédito rural e assistência técnica. Os resultados "
            "subsidiarão a revisão das NDCs do Brasil no âmbito do Acordo de Paris."
        ),
        "lattes_id": "1948372056194837",
        "autores": "Sebastião Cristiano Nunes, Teotônio Batista Ferreira, Uiara Rodrigues Costa"
    },
    92: {
        "titulo": "Estratigrafia e Análise de Bacias Sedimentares para Prospecção de Petróleo",
        "descricao": (
            "A caracterização estratigráfica detalhada de bacias sedimentares é etapa "
            "essencial na exploração de petróleo e gás natural. Este projeto realiza "
            "análise estratigráfica integrada da Bacia do Parnaíba, uma das maiores "
            "bacias sedimentares intracratônicas brasileiras, com potencial para "
            "hidrocarbonetos ainda pouco explorado. A metodologia inclui descrição "
            "sistemática de afloramentos, análise de testemunhos de sondagem, "
            "interpretação de perfis elétricos e sísmica de reflexão 2D. "
            "Serão construídos modelos estratigráficos tridimensionais das "
            "principais unidades litoestratigráficas, com identificação de "
            "sistemas deposicionais e análise de ambientes sedimentares. "
            "A caracterização petrofísica de reservatórios potenciais incluirá "
            "medidas de porosidade, permeabilidade e saturação de fluidos. "
            "Os resultados contribuirão para a compreensão da evolução "
            "tectonossedimentar da bacia e para a avaliação do seu potencial exploratório."
        ),
        "lattes_id": "4730192865473019",
        "autores": "Valdemar Luiz Assis, Walnéia Cristina Guimarães, Xerxes Rodrigues Ramos"
    },
    93: {
        "titulo": "Erosão Hídrica e Desmatamento em Bacias Hidrográficas do Cerrado",
        "descricao": (
            "A conversão de vegetação nativa do Cerrado em áreas agrícolas tem intensificado "
            "processos erosivos hídricos, com impactos sobre a produtividade dos solos e "
            "o assoreamento de corpos d'água. Este projeto quantifica as taxas de erosão "
            "hídrica superficial e entalhamento de voçorocas em bacias hidrográficas de "
            "primeira ordem no Triângulo Mineiro, sob diferentes coberturas de solo "
            "(pastagem degradada, soja convencional e Cerrado nativo). "
            "São instaladas estações hidrossedimentológicas automáticas nas bacias "
            "experimentais, com monitoramento contínuo de descarga líquida e "
            "sólida. Modelos erosivos (RUSLE e SWAT) serão calibrados e "
            "validados com os dados monitorados e utilizados para simular "
            "cenários de restauração de matas ciliares e adoção de práticas "
            "conservacionistas. Os resultados subsidiará políticas de "
            "pagamento por serviços ambientais na bacia."
        ),
        "lattes_id": "7283946015728394",
        "autores": "Yolanda Batista Lima, Zafiro Rodrigues Barros, Adélia Cristina Mota"
    },
    94: {
        "titulo": "Contaminação por Metais Pesados em Sedimentos Costeiros do NE Brasileiro",
        "descricao": (
            "Os estuários e zonas costeiras do Nordeste brasileiro recebem crescentes aportes "
            "de metais pesados provenientes de efluentes industriais, portuários e urbanos, "
            "ameaçando os ecossistemas e as populações que deles dependem para subsistência. "
            "Este projeto avalia a distribuição espacial e temporal de metais pesados "
            "(Pb, Cd, Cu, Zn, Cr, Ni, As e Hg) em sedimentos superficiais e testemunhos "
            "sedimentares de 6 estuários dos estados do Ceará e do Rio Grande do Norte. "
            "As amostras serão digeridas em micro-ondas e analisadas por ICP-MS. "
            "Os índices de geoacumulação e fator de enriquecimento serão calculados "
            "para avaliar a contribuição antrópica relativa. Bioensaios de toxicidade "
            "aguda com anfípodas e poliquetas serão realizados para avaliar a "
            "ecotoxicidade dos sedimentos contaminados. Os resultados subsidiarão "
            "a elaboração de critérios de qualidade de sedimentos costeiros "
            "para uso em licenciamento ambiental."
        ),
        "lattes_id": "3047281956304728",
        "autores": "Benedito Luiz Fonseca, Cidinha Aparecida Braga, Diógenes Rodrigues Assis"
    },
    95: {
        "titulo": "Eutrofização e Florações de Cianobactérias em Reservatórios do Semiárido",
        "descricao": (
            "Os reservatórios do semiárido nordestino são essenciais para o abastecimento "
            "humano e a irrigação agrícola, mas sofrem crescente processo de eutrofização "
            "decorrente de descargas de efluentes domésticos e agrícolas. As florações de "
            "cianobactérias produtoras de toxinas (microcistinas, cilindrospermopsinas) "
            "representam riscos graves à saúde pública. Este projeto monitora 8 "
            "reservatórios do Ceará e da Paraíba quanto a variáveis limnológicas, "
            "dinâmica da comunidade fitoplanctônica e concentrações de cianotoxinas "
            "ao longo de 2 anos. São investigados os fatores físicos, químicos e "
            "hidrológicos que determinam o florescimento das cianobactérias. "
            "Modelos preditivos de ocorrência de florações serão desenvolvidos "
            "para subsidiar sistemas de alerta precoce integrados ao "
            "monitoramento da qualidade da água para abastecimento público."
        ),
        "lattes_id": "6193847025619384",
        "autores": "Elzira Batista Cavalcanti, Fortunato Rodrigues Neto, Genoveva Cristina Lemos"
    },
    96: {
        "titulo": "Geoprocessamento e SIG para Mapeamento do Uso do Solo Urbano",
        "descricao": (
            "O monitoramento da expansão urbana e das transformações no uso e cobertura "
            "do solo é fundamental para o planejamento territorial e a gestão ambiental "
            "das cidades brasileiras. Este projeto desenvolve e aplica metodologia de "
            "mapeamento multitemporal do uso e cobertura do solo em 5 cidades médias "
            "do interior de São Paulo, integrando imagens de satélite de alta resolução "
            "(Sentinel-2, Planet), dados LiDAR e informações cadastrais municipais "
            "em ambiente de Sistema de Informação Geográfica (SIG). "
            "Algoritmos de classificação supervisionada por aprendizado de máquina "
            "(Random Forest, SVM) serão calibrados com amostras de campo. "
            "Serão gerados mapas de uso do solo para 2005, 2010, 2015 e 2023, "
            "com análise das taxas e padrões de expansão urbana, redução de áreas "
            "verdes e impermeabilização do solo. Os resultados subsidiarão a "
            "revisão dos Planos Diretores municipais participantes."
        ),
        "lattes_id": "9284730165928473",
        "autores": "Herculano Luiz Borges, Iracema Rodrigues Pinheiro, Jerônimo Batista Moreira"
    },
    97: {
        "titulo": "Fragmentação de Habitat e Corredores Ecológicos no Cerrado-Pantanal",
        "descricao": (
            "A fragmentação florestal reduz a conectividade entre populações de fauna "
            "silvestre, limitando o fluxo gênico e aumentando o risco de extinção local. "
            "Este projeto avalia a conectividade da paisagem e o potencial de corredores "
            "ecológicos na região de transição Cerrado-Pantanal no Mato Grosso do Sul, "
            "utilizando modelagem espacial e telemetria de animais silvestres. "
            "Modelos de resistência da paisagem são construídos a partir de "
            "imagens de satélite, considerando diferentes espécies-alvo: onça-parda "
            "(Puma concolor), tamanduá-bandeira (Myrmecophaga tridactyla) e "
            "queixada (Tayassu pecari). Circuitscape e análise de grafos de "
            "conectividade identificarão os corredores prioritários. "
            "Os resultados orientarão a proposta de corredores ecológicos "
            "legalmente reconhecidos e a definição de áreas prioritárias "
            "para aquisição e restauração florestal por pagamento por "
            "serviços ambientais."
        ),
        "lattes_id": "2047183956204718",
        "autores": "Katarina Cristina Farias, Laudelino Rodrigues Cruz, Margarida Batista Vieira"
    },
    98: {
        "titulo": "Dinâmica de Herbicidas no Solo: Adsorção, Mobilidade e Risco de Contaminação",
        "descricao": (
            "O uso intensivo de herbicidas na agricultura brasileira pode resultar em "
            "contaminação do solo e das águas subterrâneas quando os compostos apresentam "
            "alta mobilidade e baixa sorção. Este projeto estuda a dinâmica de quatro "
            "herbicidas amplamente utilizados no Brasil (glifosato, 2,4-D, imazetapir "
            "e metribuzim) em Latossolos e Argissolos de diferentes texturas e "
            "conteúdos de matéria orgânica. Experimentos de equilíbrio em lote "
            "determinam as isotermas de adsorção/dessorção. Colunas de solo "
            "saturadas e não-saturadas são utilizadas para determinar os "
            "parâmetros de transporte (coeficiente de dispersão, fator de "
            "retardamento) e avaliar o potencial de lixiviação. "
            "Índices de risco de contaminação são calculados e correlacionados "
            "com atributos do solo. Os resultados orientarão o uso mais "
            "seguro dos herbicidas e a adoção de práticas de manejo "
            "que reduzam o risco de contaminação ambiental."
        ),
        "lattes_id": "5193820746051938",
        "autores": "Nagib Luiz Andrade, Odélia Rodrigues Batista, Palmério Cristiano Gomes"
    },
    99: {
        "titulo": "Ilha de Calor Urbana: Monitoramento de Temperatura e Estratégias de Mitigação",
        "descricao": (
            "O fenômeno de ilha de calor urbana (ICU) resulta do aumento da temperatura "
            "nas cidades em relação às áreas rurais vizinhas, decorrente da substituição "
            "da vegetação por superfícies impermeáveis e da geração antrópica de calor. "
            "Este projeto monitora a intensidade e a distribuição espacial da ICU em "
            "três cidades do interior do Brasil (Uberlândia, Ribeirão Preto e Goiânia) "
            "por meio de redes de estações meteorológicas fixas e transectos "
            "com sensores móveis. Imagens termais dos satélites Landsat-8 e "
            "ECOSTRESS são integradas para o mapeamento da temperatura superficial. "
            "A relação entre a intensidade da ICU e indicadores de estrutura urbana "
            "(densidade de construções, fração de área verde, albedo) é modelada "
            "estatisticamente. São avaliadas estratégias de mitigação como "
            "arborização urbana, telhados verdes e pavimentos permeáveis "
            "em simulações com o modelo WRF-Urban."
        ),
        "lattes_id": "8374019265837401",
        "autores": "Querubim Batista Rocha, Roseane Rodrigues Melo, Silvano Cristiano Torres"
    },
    100: {
        "titulo": "Pressão Antrópica e Biodiversidade em Unidades de Conservação do Pantanal",
        "descricao": (
            "As unidades de conservação (UCs) do Pantanal enfrentam crescentes pressões "
            "antrópicas provenientes do entorno, incluindo desmatamento, queimadas, "
            "pecuária extensiva e caça ilegal. Este projeto avalia o estado de conservação "
            "da biodiversidade (flora, aves, mamíferos e herpetofauna) em 6 UCs do Pantanal "
            "mato-grossense, correlacionando indicadores biológicos com métricas de pressão "
            "antrópica derivadas de sensoriamento remoto e dados socioeconômicos do entorno. "
            "Inventários biológicos padronizados (transectos, armadilhas fotográficas, "
            "pontos de escuta) serão realizados em dois períodos de amostragem. "
            "Um índice integrado de integridade ecológica será desenvolvido para "
            "cada UC, permitindo priorização de ações de gestão. "
            "Os resultados subsidiarão a revisão dos planos de manejo das UCs "
            "participantes e a proposição de novas áreas protegidas nas lacunas "
            "de conservação identificadas."
        ),
        "lattes_id": "1948372560019483",
        "autores": "Teófilo Luiz Nunes, Ulmara Cristina Fonseca, Valdenice Rodrigues Lima"
    },
}


# ---------------------------------------------------------------------------
# AUTORES PARA NÃO-DUPLICATAS (ids 501-600)
# Nomes completamente distintos de qualquer nome presente em PROJECTS_DATA
# ---------------------------------------------------------------------------

NON_DUP_AUTHORS = {
    # Educação (bases 1-10)
    1:  ("4417283950441728", "Berenice Tavares Queiroz, Cássio Melo Drummond, Dulce Rodrigues Pena"),
    2:  ("5528394061552839", "Ênio Barros Cavalcante, Flávio Mota Rezende, Gláucia Dutra Paes"),
    3:  ("6639405172663940", "Hosana Correia Britto, Iranildo Luz Ferraz, Jacyra Neves Barroso"),
    4:  ("7740516283774051", "Keila Fontes Vasconcelos, Lindalva Menezes Paixão, Murilo Assis Queiroga"),
    5:  ("8851627394885162", "Neuza Diniz Cavalcante, Onofre Bispo Serrano, Perpétua Lira Tenório"),
    6:  ("9962738405996273", "Quintino Alves Paiva, Rosimeire Barreto Chaves, Silvino Farias Diniz"),
    7:  ("1073849516107384", "Tucílio Braz Serrano, Umbelina Couto Bezerra, Vanderlúcia Mota Maciel"),
    8:  ("2184950627218495", "Waldomiro Paz Vilaça, Xênia Barros Paiva, Yolanda Diniz Chaves"),
    9:  ("3295061738329506", "Zózimo Melo Tenório, Abigail Correia Serrano, Balbina Luz Paiva"),
    10: ("4306172849430617", "Celestino Farias Braz, Dorotéia Assis Vilaça, Epitácio Neves Maciel"),
    # Biologia (bases 11-20)
    11: ("5417283950541728", "Faustino Barros Chaves, Generosa Correia Tenório, Hermínio Diniz Serrano"),
    12: ("6528394061652839", "Iracilda Melo Braz, Jair Farias Vilaça, Kleide Assis Maciel"),
    13: ("7639405172763940", "Laudicéia Correia Paiva, Manassés Barros Chaves, Nazaré Diniz Tenório"),
    14: ("8750516283875051", "Odaléia Melo Serrano, Peregrino Farias Braz, Quinzinho Assis Vilaça"),
    15: ("9861627394986162", "Raimundinha Correia Maciel, Serafim Barros Paiva, Teresona Diniz Chaves"),
    16: ("1072738405107273", "Ubaldino Melo Tenório, Valdirene Farias Braz, Wlademir Assis Serrano"),
    17: ("2183849516218384", "Xenofonte Correia Vilaça, Yorlene Barros Maciel, Zacarias Diniz Paiva"),
    18: ("3294950627329495", "Abílio Melo Chaves, Belisária Farias Tenório, Clementino Assis Braz"),
    19: ("4305061738430506", "Deolinda Correia Serrano, Eudóxio Barros Vilaça, Floriza Diniz Maciel"),
    20: ("5416172849541617", "Gaudêncio Melo Paiva, Heleodora Farias Chaves, Ildefonso Assis Tenório"),
    # Computação (bases 21-30)
    21: ("6527283950652728", "Jandira Correia Braz, Kalil Barros Serrano, Leovigildo Diniz Vilaça"),
    22: ("7638394061763839", "Macrina Melo Maciel, Neraldo Farias Paiva, Olemar Assis Chaves"),
    23: ("8749405172874940", "Palmira Correia Tenório, Quesnel Barros Braz, Ramalho Diniz Serrano"),
    24: ("9850516283985051", "Sabiniana Melo Vilaça, Tacílio Farias Maciel, Umildes Assis Paiva"),
    25: ("1061627394106162", "Valquíria Correia Chaves, Wenceslau Barros Tenório, Ximenes Diniz Braz"),
    26: ("2172738405217273", "Yracema Melo Serrano, Zelinda Farias Vilaça, Amarildo Assis Maciel"),
    27: ("3283849516328384", "Benedita Correia Paiva, Carmelo Barros Chaves, Damásio Diniz Tenório"),
    28: ("4394950627439495", "Egidia Melo Braz, Felismino Farias Serrano, Guiomar Assis Vilaça"),
    29: ("5405061738540506", "Hermenegildo Correia Maciel, Igara Barros Paiva, Jovino Diniz Chaves"),
    30: ("6516172849651617", "Krauss Melo Tenório, Laudelice Farias Braz, Melchior Assis Serrano"),
    # Agronomia (bases 31-40)
    31: ("7627283950762728", "Noraldino Correia Vilaça, Orfelinda Barros Maciel, Perpetino Diniz Paiva"),
    32: ("8738394061873839", "Quirino Melo Chaves, Rosinaldo Farias Tenório, Serafina Assis Braz"),
    33: ("9849405172984940", "Telmo Correia Serrano, Urânia Barros Vilaça, Valério Diniz Maciel"),
    34: ("1050516283105051", "Walburga Melo Paiva, Xisto Farias Chaves, Yracilda Assis Tenório"),
    35: ("2161627394216162", "Zefirino Correia Braz, Adelino Barros Serrano, Barnabé Diniz Vilaça"),
    36: ("3272738405327273", "Celsina Melo Maciel, Dagoberto Farias Paiva, Eufrosina Assis Chaves"),
    37: ("4383849516438384", "Faustina Correia Tenório, Gildo Barros Braz, Hermínia Diniz Serrano"),
    38: ("5494950627549495", "Ilzete Melo Vilaça, Jucundo Farias Maciel, Kilce Assis Paiva"),
    39: ("6505061738650506", "Lazinho Correia Chaves, Melquíades Barros Tenório, Normanda Diniz Braz"),
    40: ("7616172849761617", "Olvino Melo Serrano, Perpétuo Farias Vilaça, Quininha Assis Maciel"),
    # Saúde (bases 41-50)
    41: ("8727283950872728", "Romildo Correia Paiva, Severino Barros Chaves, Tarcília Diniz Tenório"),
    42: ("9838394061983839", "Ubaldo Melo Braz, Valdivino Farias Serrano, Walcira Assis Vilaça"),
    43: ("1049405172104940", "Xicão Correia Maciel, Yraci Barros Paiva, Zulmira Diniz Chaves"),
    44: ("2150516283215051", "Abílio Melo Tenório, Benvinda Farias Braz, Crisanto Assis Serrano"),
    45: ("3261627394326162", "Dagoberta Correia Vilaça, Euclídes Barros Maciel, Firmino Diniz Paiva"),
    46: ("4372738405437273", "Griselda Melo Chaves, Hamilcar Farias Tenório, Ignácio Assis Braz"),
    47: ("5483849516548384", "Jocasta Correia Serrano, Kildere Barros Vilaça, Lindaura Diniz Maciel"),
    48: ("6594950627659495", "Marcílio Melo Paiva, Nerilda Farias Chaves, Odalécio Assis Tenório"),
    49: ("7605061738760506", "Palmério Correia Braz, Quirinaldo Barros Serrano, Rosaura Diniz Vilaça"),
    50: ("8716172849871617", "Salustiano Melo Maciel, Tancredo Farias Paiva, Umbelino Assis Chaves"),
    # Ciências Sociais (bases 51-60)
    51: ("9827283950982728", "Valdívia Correia Tenório, Walmiro Barros Braz, Xênia Diniz Serrano"),
    52: ("1038394061103839", "Yrene Melo Vilaça, Zelão Farias Maciel, Abelino Assis Paiva"),
    53: ("2149405172214940", "Benedinha Correia Chaves, Cândido Barros Tenório, Doroteu Diniz Braz"),
    54: ("3250516283325051", "Elzirita Melo Serrano, Fulgêncio Farias Vilaça, Gumercindo Assis Maciel"),
    55: ("4361627394436162", "Honorinda Correia Paiva, Irenaldo Barros Chaves, Jerônima Diniz Tenório"),
    56: ("5472738405547273", "Kubitschek Melo Braz, Leodomiro Farias Serrano, Malvina Assis Vilaça"),
    57: ("6583849516658384", "Napoleão Correia Maciel, Ondina Barros Paiva, Policarpo Diniz Chaves"),
    58: ("7694950627769495", "Quirinaldo Melo Tenório, Raimundino Farias Braz, Servilha Assis Serrano"),
    59: ("8705061738870506", "Teofilindo Correia Vilaça, Uldarico Barros Maciel, Valdomira Diniz Paiva"),
    60: ("9816172849981617", "Walmira Melo Chaves, Xirlene Farias Tenório, Ytalmar Assis Braz"),
    # Engenharia (bases 61-70)
    61: ("1027283950102728", "Zacarias Correia Serrano, Acácia Barros Vilaça, Belisário Diniz Maciel"),
    62: ("2138394061213839", "Celsino Melo Paiva, Delmira Farias Chaves, Edmilsa Assis Tenório"),
    63: ("3249405172324940", "Falcão Correia Braz, Gentileza Barros Serrano, Hédio Diniz Vilaça"),
    64: ("4350516283435051", "Irenita Melo Maciel, Jandaíra Farias Paiva, Katucha Assis Chaves"),
    65: ("5461627394546162", "Lidiane Correia Tenório, Marcolino Barros Braz, Natanael Diniz Serrano"),
    66: ("6572738405657273", "Olegário Melo Vilaça, Pacífica Farias Maciel, Quiroga Assis Paiva"),
    67: ("7683849516768384", "Raimundino Correia Chaves, Salvelina Barros Tenório, Torquato Diniz Braz"),
    68: ("8794950627879495", "Ubaldina Melo Serrano, Valentim Farias Vilaça, Wergílio Assis Maciel"),
    69: ("9805061738980506", "Xenira Correia Paiva, Yolandinha Barros Chaves, Zacaria Diniz Tenório"),
    70: ("1016172849101617", "Abivaldo Melo Braz, Belmiro Farias Serrano, Celuta Assis Vilaça"),
    # Letras (bases 71-80)
    71: ("2127283950212728", "Domingos Correia Maciel, Eufêmia Barros Paiva, Fidelis Diniz Chaves"),
    72: ("3238394061323839", "Getulio Melo Tenório, Hortência Farias Braz, Idalgo Assis Serrano"),
    73: ("4349405172434940", "Jucélia Correia Vilaça, Kelme Barros Maciel, Leocádia Diniz Paiva"),
    74: ("5450516283545051", "Marcionílio Melo Chaves, Noêmia Farias Tenório, Osvaldo Assis Braz"),
    75: ("6561627394656162", "Patrocínio Correia Serrano, Querubina Barros Vilaça, Rincão Diniz Maciel"),
    76: ("7672738405767273", "Salustiana Melo Paiva, Telmindo Farias Chaves, Urânia Assis Tenório"),
    77: ("8783849516878384", "Valdomiro Correia Braz, Waltercina Barros Serrano, Xildete Diniz Vilaça"),
    78: ("9894950627989495", "Yolanda Melo Maciel, Zacaria Farias Paiva, Abimael Assis Chaves"),
    79: ("1005061738100506", "Belquior Correia Tenório, Celcino Barros Braz, Dinalva Diniz Serrano"),
    80: ("2116172849211617", "Elenita Melo Vilaça, Flauzino Farias Maciel, Gessilda Assis Paiva"),
    # Exatas (bases 81-90)
    81: ("3227283950322728", "Helvécio Correia Chaves, Ilzamar Barros Tenório, Jerusa Diniz Braz"),
    82: ("4338394061433839", "Kléber Melo Serrano, Laudelino Farias Vilaça, Meire Assis Maciel"),
    83: ("5449405172544940", "Nicanor Correia Paiva, Onésimo Barros Chaves, Pacífico Diniz Tenório"),
    84: ("6550516283655051", "Quitíldes Melo Braz, Ramaldes Farias Serrano, Silvanira Assis Vilaça"),
    85: ("7661627394766162", "Teomário Correia Maciel, Udinalva Barros Paiva, Valterino Diniz Chaves"),
    86: ("8772738405877273", "Wanderlan Melo Tenório, Xeraldo Farias Braz, Yolane Assis Serrano"),
    87: ("9883849516988384", "Zuleido Correia Vilaça, Adarilson Barros Maciel, Belarmina Diniz Paiva"),
    88: ("1094950627109495", "Clenilton Melo Chaves, Dinalvo Farias Tenório, Ezequiela Assis Braz"),
    89: ("2105061738210506", "Felisberto Correia Serrano, Gumercinda Barros Vilaça, Heraldo Diniz Maciel"),
    90: ("3216172849321617", "Iduina Melo Paiva, Jacildo Farias Chaves, Kezinha Assis Tenório"),
    # Ambiental (bases 91-100)
    91: ("4327283950432728", "Lincomar Correia Braz, Madaleno Barros Serrano, Natalício Diniz Vilaça"),
    92: ("5438394061543839", "Ofenísia Melo Maciel, Pascoalino Farias Paiva, Quelzia Assis Chaves"),
    93: ("6549405172654940", "Roldão Correia Tenório, Sabinaldo Barros Braz, Talvina Diniz Serrano"),
    94: ("7650516283765051", "Ulcira Melo Vilaça, Valdomir Farias Maciel, Wagna Assis Paiva"),
    95: ("8761627394876162", "Xênia Correia Chaves, Yvonaldo Barros Tenório, Zacarias Diniz Braz"),
    96: ("9872738405987273", "Agenor Melo Serrano, Belquis Farias Vilaça, Cinalda Assis Maciel"),
    97: ("1083849516108384", "Dagoberto Correia Paiva, Elzivanda Barros Chaves, Fabricio Diniz Tenório"),
    98: ("2194950627219495", "Genivaldo Melo Braz, Hildegarda Farias Serrano, Iracildo Assis Vilaça"),
    99: ("3205061738320506", "Jucineide Correia Maciel, Kalildo Barros Paiva, Lourdinha Diniz Chaves"),
   100: ("4316172849431617", "Misael Melo Tenório, Normanda Farias Braz, Osvaldina Assis Serrano"),
}


def make_v3(base: dict, new_id: int) -> dict:
    """Gera a 3ª duplicata (sem descrição) – ids 301-400."""
    titulo = base["titulo"]
    lattes = base["lattes_id"]
    autores = base["autores"]

    mod = (new_id - 300) % 10

    # Variação sutil no título
    titulo_v3 = titulo
    suffixes = [
        " - Relatório Final", " - Edição Revisada", " - Versão Atualizada",
        " - Segundo Ciclo", " - Nova Fase", " - Continuidade",
        " - Etapa II", " - Fase 2", " - Renovação", " - Extensão",
    ]
    titulo_v3 = titulo_v3.rstrip(".") + suffixes[mod]

    # Autores: mesmo conjunto com variação de formato
    parts = [a.strip() for a in autores.split(",")]
    if mod % 3 == 0:
        # Inverte sobrenome/nome no primeiro autor
        words = parts[0].split()
        if len(words) >= 2:
            parts[0] = words[-1].upper() + ", " + " ".join(words[:-1])
    elif mod % 3 == 1:
        # Coloca todos em maiúsculas
        parts = [p.upper() for p in parts]
    # else: mantém como está

    return {
        "id": new_id,
        "titulo_projeto": titulo_v3,
        "descricao_projeto": "",
        "lattes_ids": lattes,
        "nomes_integrante": ", ".join(parts),
    }


def make_v4(base: dict, new_id: int) -> dict:
    """Gera a 4ª duplicata (1 autor apenas) – ids 401-500."""
    titulo = base["titulo"]
    descricao = base["descricao"]
    lattes = base["lattes_id"]
    autores = base["autores"]

    mod = (new_id - 400) % 10

    # Título: mesma variação sutil da v1
    titulo_v4 = titulo
    if mod in (0, 1):
        titulo_v4 = titulo_v4.upper()
    elif mod in (2, 3):
        titulo_v4 = titulo_v4.replace(" - ", ": ", 1)
    elif mod in (4, 5):
        titulo_v4 = titulo_v4.rstrip(".") + "."
    else:
        titulo_v4 = titulo_v4.replace("e ", "& ", 1) if " e " in titulo_v4 else titulo_v4

    # Descrição: mesma variação da v1
    descricao_v4 = descricao
    replacements = [
        ("O presente projeto", "O referido projeto"),
        ("tem como objetivo", "tem por objetivo"),
        ("serão realizadas", "serão efetuadas"),
        ("contribuirão para", "irão contribuir para"),
        ("A metodologia", "A metodologia adotada"),
        ("Este projeto", "O presente projeto"),
        ("com o objetivo", "com o propósito"),
        ("por meio de", "através de"),
        ("O projeto investiga", "O presente projeto investiga"),
        ("O projeto avalia", "O presente projeto avalia"),
        ("Serão aplicados", "Serão utilizados"),
        ("Os resultados deverão", "Os resultados obtidos deverão"),
    ]
    for old, new in replacements:
        if old in descricao_v4:
            descricao_v4 = descricao_v4.replace(old, new, 1)
            break

    # Apenas 1 autor (escolhe pelo mod)
    parts = [a.strip() for a in autores.split(",")]
    autor_unico = parts[mod % len(parts)]

    return {
        "id": new_id,
        "titulo_projeto": titulo_v4,
        "descricao_projeto": descricao_v4,
        "lattes_ids": lattes,
        "nomes_integrante": autor_unico,
    }


def make_non_dup(base: dict, new_id: int, base_id: int) -> dict:
    """Gera não-duplicata (ids 501-600): conteúdo muito similar, autores completamente diferentes."""
    titulo = base["titulo"]
    descricao = base["descricao"]

    mod = (new_id - 500) % 10

    # Título: mesma variação da v1 (muito semelhante)
    titulo_nd = titulo
    if mod in (0, 1):
        titulo_nd = titulo_nd.replace(" - ", ": ", 1)
    elif mod in (2, 3):
        titulo_nd = titulo_nd.rstrip(".") + "."
    elif mod in (4, 5):
        titulo_nd = titulo_nd.replace("e ", "& ", 1) if " e " in titulo_nd else titulo_nd
    # else: mantém como está

    # Descrição: mesma variação da v2 (similar mas levemente parafraseada)
    descricao_nd = descricao
    paraphrases = [
        ("O presente projeto tem como objetivo", "Esta pesquisa objetiva"),
        ("tem como objetivo principal", "visa prioritariamente"),
        ("tem como objetivo", "busca"),
        ("tem por objetivo", "objetiva"),
        ("Este projeto tem como objetivo", "A proposta tem por finalidade"),
        ("contribuirão para", "possibilitarão"),
        ("Os resultados contribuirão", "Os achados subsidiarão"),
        ("A metodologia inclui", "O percurso metodológico prevê"),
        ("Serão realizados", "Estão previstos"),
        ("serão realizadas", "serão executadas"),
        ("por meio de", "mediante"),
        ("O projeto investiga", "A pesquisa investiga"),
        ("O projeto avalia", "O estudo avalia"),
        ("O projeto desenvolve", "A proposta desenvolve"),
        ("O projeto analisa", "O trabalho analisa"),
        ("Serão aplicados", "Serão utilizados"),
        ("Os resultados deverão", "Os resultados obtidos deverão"),
        ("O delineamento metodológico", "O planejamento metodológico"),
    ]
    for old, new in paraphrases:
        if old in descricao_nd:
            descricao_nd = descricao_nd.replace(old, new, 1)
            break

    # Autores e lattes completamente diferentes
    new_lattes, new_autores = NON_DUP_AUTHORS[base_id]

    return {
        "id": new_id,
        "titulo_projeto": titulo_nd,
        "descricao_projeto": descricao_nd,
        "lattes_ids": new_lattes,
        "nomes_integrante": new_autores,
    }


def make_duplicate_v1(base: dict, new_id: int) -> dict:
    """Gera a primeira duplicata (ruído baixo) de um projeto base."""
    titulo = base["titulo"]
    descricao = base["descricao"]
    lattes = base["lattes_id"]
    autores = base["autores"]

    # Variações sutis por módulo do id base
    mod = (new_id - 100) % 10

    # Variações no título
    titulo_v1 = titulo
    if mod in (0, 1):
        titulo_v1 = titulo_v1.upper()
    elif mod in (2, 3):
        titulo_v1 = titulo_v1.replace(" - ", ": ", 1)
    elif mod in (4, 5):
        # remove código no início se houver
        parts = titulo_v1.split(" - ", 1)
        if len(parts) == 2:
            titulo_v1 = parts[0].replace(".", ",") + " - " + parts[1]
    elif mod in (6, 7):
        titulo_v1 = titulo_v1.rstrip(".") + "."
    else:
        titulo_v1 = titulo_v1.replace("e ", "& ", 1) if " e " in titulo_v1 else titulo_v1

    # Variações na descrição (pequenas)
    descricao_v1 = descricao
    replacements_v1 = [
        ("O presente projeto", "O referido projeto"),
        ("tem como objetivo", "tem por objetivo"),
        ("serão realizadas", "serão efetuadas"),
        ("contribuirão para", "irão contribuir para"),
        ("os resultados", "Os resultados"),
        ("A metodologia", "A metodologia adotada"),
        ("Este projeto", "O presente projeto"),
        ("com o objetivo", "com o propósito"),
        ("por meio de", "através de"),
        ("a partir de", "com base em"),
        # Padrões adicionais para garantir cobertura
        ("O projeto investiga", "O presente projeto investiga"),
        ("O projeto avalia", "O presente projeto avalia"),
        ("O projeto desenvolve", "O presente projeto desenvolve"),
        ("O projeto realiza", "O presente projeto realiza"),
        ("O projeto analisa", "O presente projeto analisa"),
        ("O projeto propõe", "O presente projeto propõe"),
        ("O projeto tem como", "O presente trabalho tem como"),
        ("Serão aplicados", "Serão utilizados"),
        ("serão aplicados", "serão utilizados"),
        ("Os resultados deverão", "Os resultados obtidos deverão"),
        ("O delineamento metodológico", "O planejamento metodológico"),
        ("A resistência", "A resistência bacteriana"),
        ("A pesquisa será conduzida", "O estudo será conduzido"),
        ("A pesquisa adota", "O estudo adota"),
        ("São instaladas", "Foram instaladas"),
        ("São investigados", "Foram investigados"),
        ("O manejo adequado", "O manejo correto"),
        ("O tratamento de", "O processo de tratamento de"),
        ("O dataset de", "O conjunto de dados de"),
    ]
    replaced = False
    for old, new in replacements_v1:
        if old in descricao_v1:
            descricao_v1 = descricao_v1.replace(old, new, 1)
            replaced = True
            break
    # Fallback garantido: adiciona nota de rodapé ao final
    if not replaced:
        descricao_v1 = descricao_v1.rstrip() + " O projeto conta com aprovação do Comitê de Ética institucional."

    # Variações nos autores (formato)
    autores_v1 = autores
    if ", " in autores_v1:
        parts = [a.strip() for a in autores_v1.split(",")]
        # Maiúscula no primeiro ou todos maiúsculos para alguns
        if mod % 2 == 0:
            parts = [p.upper() if i == 0 else p for i, p in enumerate(parts)]
        else:
            parts = [p.title() if p.isupper() else p for p in parts]
        autores_v1 = ", ".join(parts)

    # Pequena variação no lattes_id (simula erro de digitação ocasionalmente)
    lattes_v1 = lattes
    if mod in (3, 7):
        lattes_v1 = lattes[:-1] + str((int(lattes[-1]) + 1) % 10)

    return {
        "id": new_id,
        "titulo_projeto": titulo_v1,
        "descricao_projeto": descricao_v1,
        "lattes_ids": lattes_v1,
        "nomes_integrante": autores_v1,
    }


def make_duplicate_v2(base: dict, new_id: int) -> dict:
    """Gera a segunda duplicata (ruído moderado) de um projeto base."""
    titulo = base["titulo"]
    descricao = base["descricao"]
    lattes = base["lattes_id"]
    autores = base["autores"]

    mod = (new_id - 200) % 10

    # Variações moderadas no título
    titulo_v2 = titulo
    titulo_v2 = titulo_v2.replace("Melhoramento", "Desenvolvimento")
    titulo_v2 = titulo_v2.replace("Avaliação", "Análise")
    titulo_v2 = titulo_v2.replace("Estudo", "Investigação")
    titulo_v2 = titulo_v2.replace("Formação", "Capacitação")
    titulo_v2 = titulo_v2.replace("Levantamento", "Inventário")
    titulo_v2 = titulo_v2.replace("Caracterização", "Avaliação")
    titulo_v2 = titulo_v2.replace("Monitoramento", "Vigilância")
    titulo_v2 = titulo_v2.replace("Implementação", "Implantação")
    # Se nada mudou, adiciona subtítulo
    if titulo_v2 == titulo:
        titulo_v2 = titulo_v2 + " - Estudo de Caso"

    # Paráfrase moderada da descrição
    descricao_v2 = descricao
    paraphrases = [
        ("tem como objetivo principal", "visa prioritariamente"),
        ("tem como objetivo", "busca"),
        ("tem por objetivo", "objetiva"),
        ("contribuindo para o conhecimento", "ampliando o entendimento"),
        ("contribuirão para", "possibilitarão"),
        ("irão contribuir para", "auxiliarão no"),
        ("Os resultados esperados incluem", "Como resultados, espera-se"),
        ("Os resultados contribuirão", "Os achados subsidiarão"),
        ("A metodologia inclui", "O percurso metodológico prevê"),
        ("A metodologia adotada inclui", "A abordagem metodológica compreende"),
        ("Serão realizados", "Estão previstos"),
        ("serão realizadas", "serão executadas"),
        ("serão avaliados", "serão mensurados"),
        ("Serão avaliados", "Serão mensurados"),
        ("Este projeto tem como objetivo", "A proposta tem por finalidade"),
        ("O presente projeto tem como objetivo", "Esta pesquisa objetiva"),
        ("O referido projeto tem por objetivo", "O trabalho tem como meta"),
        ("A pesquisa será conduzida", "O estudo será desenvolvido"),
        ("Os experimentos serão conduzidos", "Os ensaios serão realizados"),
        ("por meio de", "mediante"),
        ("através de", "por intermédio de"),
        ("com base em", "fundamentado em"),
        # Padrões adicionais
        ("O projeto investiga", "A pesquisa investiga"),
        ("O projeto avalia", "O estudo avalia"),
        ("O projeto desenvolve", "A proposta desenvolve"),
        ("O projeto realiza", "A equipe realiza"),
        ("O projeto analisa", "O trabalho analisa"),
        ("O projeto propõe", "O estudo propõe"),
        ("O projeto sintetiza", "O trabalho sintetiza"),
        ("O projeto quantifica", "O estudo quantifica"),
        ("O projeto monitora", "O trabalho acompanha"),
        ("O projeto documenta", "A pesquisa registra"),
        ("O dataset de treinamento", "A base de dados de treinamento"),
        ("O manejo adequado", "O manejo correto e adequado"),
        ("O tratamento de efluentes", "O processamento de efluentes"),
        ("A resistência bacteriana a antibióticos convencionais", "A resistência de bactérias a antibióticos tradicionais"),
        ("Os biorreatores", "Os sistemas de biorreatores"),
        ("A produção de biocombustíveis", "A geração de biocombustíveis"),
        ("O monitoramento contínuo", "O acompanhamento contínuo"),
        ("Os materiais compósitos", "Os materiais compostos"),
        ("A segregação residencial", "A segregação habitacional"),
        ("Os povos indígenas", "As populações indígenas"),
    ]
    changed = False
    for old, new in paraphrases:
        if old in descricao_v2:
            descricao_v2 = descricao_v2.replace(old, new, 1)
            changed = True

    # Segunda rodada de paráfrases
    paraphrases2 = [
        ("para a melhoria", "para o aprimoramento"),
        ("no contexto", "no âmbito"),
        ("ao longo de", "durante"),
        ("no Sul do Brasil", "na Região Sul do País"),
        ("no Brasil", "no território nacional"),
        ("na região", "na área"),
        ("Espera-se", "Espera-se que"),
        ("Os resultados", "As conclusões"),
        ("com o objetivo de", "a fim de"),
        ("incluindo", "compreendendo"),
    ]
    for old, new in paraphrases2:
        if old in descricao_v2:
            descricao_v2 = descricao_v2.replace(old, new, 1)
            changed = True

    # Trunca levemente (±20%) para simular reescrita
    sentences = descricao_v2.split(". ")
    if len(sentences) > 5 and mod < 4:
        sentences = sentences[:-2]  # remove últimas 2 frases
        descricao_v2 = ". ".join(sentences) + "."
        changed = True
    elif len(sentences) > 3 and mod >= 6:
        sentences = sentences[1:]  # remove primeira frase
        descricao_v2 = ". ".join(sentences)
        changed = True

    # Fallback garantido para v2
    if not changed:
        descricao_v2 = descricao_v2.rstrip() + (
            " Os resultados serão apresentados em relatórios técnicos e artigos científicos."
        )

    # Variações nos autores (pode faltar 1 ou ter formato diferente)
    autores_v2 = autores
    parts = [a.strip() for a in autores_v2.split(",")]
    if len(parts) > 2 and mod in (2, 5, 8):
        parts = parts[:-1]  # remove último autor
    # Inverte formato de um autor
    if mod in (1, 4, 7) and len(parts) > 0:
        name = parts[0]
        words = name.split()
        if len(words) >= 2:
            parts[0] = words[-1].upper() + ", " + " ".join(words[:-1])
    autores_v2 = ", ".join(parts)

    # Lattes com variação maior
    lattes_v2 = lattes
    if mod in (0, 4, 8):
        lattes_v2 = lattes[:-2] + str((int(lattes[-2]) + 1) % 10) + str((int(lattes[-1]) + 2) % 10)

    return {
        "id": new_id,
        "titulo_projeto": titulo_v2,
        "descricao_projeto": descricao_v2,
        "lattes_ids": lattes_v2,
        "nomes_integrante": autores_v2,
    }


def make_base(proj_id: int) -> dict:
    data = PROJECTS_DATA[proj_id]
    return {
        "id": proj_id,
        "titulo_projeto": data["titulo"],
        "descricao_projeto": data["descricao"],
        "lattes_ids": data["lattes_id"],
        "nomes_integrante": data["autores"],
    }


def generate_batch(batch_num: int) -> list:
    """Lotes 1-10: base + v1 + v2 (ids 1-300)."""
    start = (batch_num - 1) * 10 + 1
    end = batch_num * 10
    results = []
    for i in range(start, end + 1):
        base = PROJECTS_DATA[i]
        results.append(make_base(i))
        results.append(make_duplicate_v1(base, i + 100))
        results.append(make_duplicate_v2(base, i + 200))
    return results


def generate_ext_batch(batch_num: int) -> list:
    """Lotes 11-20: v3 + v4 + non-dup (ids 301-600).
    Lote 11 → bases 1-10, lote 12 → bases 11-20, ..., lote 20 → bases 91-100."""
    base_start = (batch_num - 11) * 10 + 1
    base_end = base_start + 9
    results = []
    for i in range(base_start, base_end + 1):
        base = PROJECTS_DATA[i]
        results.append(make_v3(base, i + 300))
        results.append(make_v4(base, i + 400))
        results.append(make_non_dup(base, i + 500, i))
    return results


def get_batch_file(batch_num: int) -> str:
    return os.path.join(CACHE_DIR, f"test_batch_{batch_num:02d}.json")


def show_status():
    print("Status dos lotes:")
    print("  --- Lotes 1-10: base + v1 + v2 (ids 1-300) ---")
    for b in range(1, 11):
        path = get_batch_file(b)
        start = (b - 1) * 10 + 1
        end = b * 10
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            print(f"  Lote {b:02d} (bases {start:3d}-{end:3d}): OK ({len(data)} projetos)")
        else:
            print(f"  Lote {b:02d} (bases {start:3d}-{end:3d}): PENDENTE")
    print("  --- Lotes 11-20: v3 + v4 + non-dup (ids 301-600) ---")
    for b in range(11, 21):
        path = get_batch_file(b)
        base_start = (b - 11) * 10 + 1
        base_end = base_start + 9
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            print(f"  Lote {b:02d} (bases {base_start:3d}-{base_end:3d}): OK ({len(data)} projetos)")
        else:
            print(f"  Lote {b:02d} (bases {base_start:3d}-{base_end:3d}): PENDENTE")


def merge_batches():
    all_projects = []
    missing = []
    for b in range(1, 21):
        path = get_batch_file(b)
        if not os.path.exists(path):
            missing.append(b)
        else:
            with open(path) as f:
                all_projects.extend(json.load(f))

    if missing:
        print(f"Lotes pendentes: {missing}. Gere-os antes de mesclar.")
        return False

    all_projects.sort(key=lambda x: x["id"])
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)
    print(f"Mesclado com sucesso: {len(all_projects)} projetos em {OUTPUT_FILE}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Gerador incremental de test.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--batch", type=int, choices=range(1, 21), metavar="N",
                       help="Gera lote N (1-10: base+v1+v2 | 11-20: v3+v4+non-dup)")
    group.add_argument("--merge", action="store_true",
                       help="Mescla todos os lotes (1-20) em cache/test.json")
    group.add_argument("--status", action="store_true",
                       help="Mostra status dos lotes")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.merge:
        merge_batches()
    elif args.batch:
        b = args.batch
        path = get_batch_file(b)
        if b <= 10:
            data = generate_batch(b)
            base_start = (b - 1) * 10 + 1
            base_end = b * 10
            desc = f"bases {base_start}-{base_end} → ids {base_start}-{base_end}, {base_start+100}-{base_end+100}, {base_start+200}-{base_end+200}"
        else:
            data = generate_ext_batch(b)
            base_start = (b - 11) * 10 + 1
            base_end = base_start + 9
            desc = f"bases {base_start}-{base_end} → ids {base_start+300}-{base_end+300}, {base_start+400}-{base_end+400}, {base_start+500}-{base_end+500}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Lote {b:02d} gerado: {desc} ({len(data)} projetos) → {path}")


if __name__ == "__main__":
    main()
