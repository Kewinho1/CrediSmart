#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera relatorio PDF de 8 paginas a partir dos resultados reais do main.py."""
import json, math
from pathlib import Path
from xml.sax.saxutils import escape

# A geração do PDF sempre executa novamente o pipeline. Assim, as figuras são
# criadas pelo Matplotlib a partir da execução atual, sem reutilizar PNGs antigos.
from main import main as executar_experimento
executar_experimento()

import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

R = Path(__file__).resolve().parent
D = json.loads((R/'resultados.json').read_text(encoding='utf-8'))
FIG_DIR = R / D['figuras_dir']
OUT = R / 'relatorio_tecnico.pdf'
W,H = A4
M = 48
CW = W - 2*M
NAVY=colors.HexColor('#14263c')
BLUE=colors.HexColor('#2e5f9d')
TEAL=colors.HexColor('#159f91')
INK=colors.HexColor('#253247')
MUTED=colors.HexColor('#607085')
LT=colors.HexColor('#eef3f8')
RULE=colors.HexColor('#dbe4ec')
WHITE=colors.white

# Linux costuma trazer DejaVu. Em outros sistemas, o ReportLab fornece
# fontes Vera compatíveis, evitando depender de /usr/share/fonts no Windows.
fonte_dejavu = Path('/usr/share/fonts/truetype/dejavu')
if (fonte_dejavu / 'DejaVuSans.ttf').exists():
    regular, negrito = (fonte_dejavu / 'DejaVuSans.ttf',
                        fonte_dejavu / 'DejaVuSans-Bold.ttf')
else:
    pasta_fontes = Path(reportlab.__file__).resolve().parent / 'fonts'
    regular, negrito = (pasta_fontes / 'Vera.ttf', pasta_fontes / 'VeraBd.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', str(regular)))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', str(negrito)))
pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold')

body=ParagraphStyle('body',fontName='DejaVu',fontSize=9.15,leading=15.0,textColor=INK,spaceAfter=0)
small=ParagraphStyle('small',parent=body,fontSize=8.1,leading=12.9)
mini=ParagraphStyle('mini',parent=body,fontSize=7.5,leading=11.3)
caption=ParagraphStyle('caption',parent=body,fontSize=8,leading=12,textColor=MUTED)
bullet=ParagraphStyle('bullet',parent=body,fontSize=8.8,leading=14,leftIndent=12,firstLineIndent=-9)

c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('CrediSmart | Sistema hibrido de decisao de credito')
c.setAuthor('Grupo CrediSmart - identificacao pendente')
y=H-M
page=0


def fmt(x,d=3):
    return f'{x:.{d}f}'.replace('.',',')
def pct(x): return f'{x*100:.1f}%'.replace('.',',')
def moeda(x):return 'R$ '+f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')


def newpage(chapter, title, label=None):
    global page,y
    if page:c.showPage()
    page += 1
    c.setFillColor(NAVY);c.rect(0,H-18,W,18,stroke=0,fill=1)
    c.setFont('DejaVu-Bold',8.5);c.setFillColor(NAVY)
    c.drawString(M,H-44,'CREDISMART  /  RELATÓRIO TÉCNICO')
    c.setFont('DejaVu',8);c.setFillColor(MUTED)
    c.drawRightString(W-M,H-44,'UniAnchieta  ·  IA  ·  2026/2')
    c.setStrokeColor(RULE);c.line(M,H-51,W-M,H-51)
    c.setFont('DejaVu-Bold',9.4);c.setFillColor(TEAL)
    c.drawString(M,H-82,chapter.upper())
    c.setFont('DejaVu-Bold',20);c.setFillColor(NAVY)
    c.drawString(M,H-111,title)
    if label:
        c.setFont('DejaVu',9);c.setFillColor(MUTED);c.drawString(M,H-127,label)
        y=H-148
    else: y=H-137
    c.setStrokeColor(RULE);c.line(M,34,W-M,34)
    c.setFont('DejaVu',7.6);c.setFillColor(MUTED)
    c.drawString(M,22,'Base sintética · implementação acadêmica · não utilizar para concessão real')
    c.drawRightString(W-M,22,f'{page:02d} / 08')


def para(txt,kind='body',gap=9,width=None):
    global y
    style={'body':body,'small':small,'mini':mini,'caption':caption,'bullet':bullet}[kind]
    w = CW if width is None else width
    p=Paragraph(txt,style)
    _,h=p.wrap(w,1000)
    p.drawOn(c,M,y-h)
    y-=h+gap
    if y<43: print('AVISO: texto chegou baixo',page,y)
    return h


def head(text,gap=7):
    global y
    y-=3
    c.setFont('DejaVu-Bold',11.6);c.setFillColor(BLUE)
    c.drawString(M,y-11,text)
    y-=24+gap


def line():
    global y
    c.setStrokeColor(RULE);c.line(M,y,W-M,y)
    y-=13


def figure(name,width=CW,height=None,captiontext=None):
    global y
    p=FIG_DIR/name
    im=ImageReader(str(p));iw,ih=im.getSize()
    if height is None: height=width*ih/iw
    c.drawImage(im,M,y-height,width=width,height=height,mask='auto')
    y-=height+5
    if captiontext:para(captiontext,'caption',gap=10)


def tab(rows,widths=None,align='LEFT',font_size=8.1,row_pad=7,header=True,highlight_last=False):
    global y
    if widths is None:widths=[CW/len(rows[0])]*len(rows[0])
    t=Table(rows,colWidths=widths,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),
          ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),row_pad),
          ('BOTTOMPADDING',(0,0),(-1,-1),row_pad),
          ('FONTNAME',(0,0),(-1,-1),'DejaVu'),('FONTSIZE',(0,0),(-1,-1),font_size),
          ('TEXTCOLOR',(0,0),(-1,-1),INK),('LINEBELOW',(0,-1),(-1,-1),.7,RULE),
          ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,colors.HexColor('#f6f9fc')]),
          ('ALIGN',(0,0),(-1,-1),align)]
    if header:
        cmds += [('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),WHITE),
                 ('FONTNAME',(0,0),(-1,0),'DejaVu-Bold')]
    if highlight_last:cmds+=[('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#e6f7f2'))]
    t.setStyle(TableStyle(cmds));_,h=t.wrap(CW,1000)
    t.drawOn(c,M,y-h);y-=h+10
    if y<43: print('AVISO: tabela chegou baixo',page,y)
    return h


def boxmetric(label,val,x0,width=155):
    c.setFillColor(LT);c.roundRect(x0,y-65,width,60,7,fill=1,stroke=0)
    c.setFont('DejaVu',8.0);c.setFillColor(MUTED);c.drawString(x0+11,y-22,label)
    c.setFont('DejaVu-Bold',20);c.setFillColor(NAVY);c.drawString(x0+11,y-47,val)

# CAPA
page=1
c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(BLUE);c.rect(0,H-20,W,20,fill=1,stroke=0)
c.setFillColor(TEAL);c.rect(M,H-188,70,5,fill=1,stroke=0)
c.setFont('DejaVu-Bold',12);c.setFillColor(colors.HexColor('#a8c7e3'))
c.drawString(M,H-115,'CENTRO UNIVERSITÁRIO PADRE ANCHIETA')
c.setFont('DejaVu',10);c.drawString(M,H-142,'Inteligência Artificial  ·  2º semestre de 2026')
c.setFont('DejaVu-Bold',37);c.setFillColor(WHITE)
c.drawString(M,H-252,'CrediSmart')
c.setFont('DejaVu-Bold',17);c.drawString(M,H-287,'Sistema híbrido de decisão de crédito')
c.setFont('DejaVu',11);c.setFillColor(colors.HexColor('#d4e4f1'))
c.drawString(M,H-317,'Rede neural MLP + inferência fuzzy Mamdani + algoritmo genético')
coverbox_y=H-390
c.setFillColor(colors.HexColor('#203c58'));c.roundRect(M,coverbox_y-160,CW,160,12,fill=1,stroke=0)
for i,(lab,v) in enumerate([('AMOSTRAS','2.000'),('F1 MLP MANUAL','81,6%'),('F1 MLP OTIMIZADA','85,6%')]):
    x=M+22+i*157
    c.setFont('DejaVu',8.2);c.setFillColor(colors.HexColor('#bad1e6'))
    c.drawString(x,coverbox_y-42,lab)
    c.setFont('DejaVu-Bold',23);c.setFillColor(WHITE)
    c.drawString(x,coverbox_y-78,v)
c.setFont('DejaVu',9.4);c.setFillColor(WHITE)
c.drawString(M+22,coverbox_y-124,'Resultados reproduzíveis usando os dados e sementes do enunciado.')
c.setFont('DejaVu-Bold',9.5);c.setFillColor(colors.HexColor('#8edbce'))
c.drawString(M,212,'IDENTIFICAÇÃO DO GRUPO')
c.setFont('DejaVu',10);c.setFillColor(WHITE)
for j,txt in enumerate(['Aluno(a) 1: ________________________  RA: ______________',
                        'Aluno(a) 2: ________________________  RA: ______________',
                        'Aluno(a) 3: ________________________  RA: ______________']):
    c.drawString(M,188-j*25,txt)
c.setFont('DejaVu',9);c.setFillColor(colors.HexColor('#a8c7e3'))
c.drawString(M,64,'Relatório de projeto acadêmico  ·  16 de novembro de 2026')
c.drawString(M,46,'Revisar identificação e declaração de uso de IA antes de entregar.')

# PAGE 2
newpage('01 / Introdução e metodologia','Problema, dados e aprendizagem')
para('<b>Objetivo.</b> Investigar um processo automatizado de análise de crédito em três estágios: uma MLP estima P(inadimplência), um controlador fuzzy transforma o risco e o comprometimento de renda em percentual de limite, e um algoritmo genético busca hiperparâmetros da MLP. Todos os componentes centrais foram implementados manualmente com NumPy.')
head('Base sintética e prevenção de vazamento')
para('A função <b>gerar_dados(n=2000, seed=2026)</b> foi copiada do enunciado. As variáveis são renda, idade, comprometimento de renda, atrasos nos últimos 12 meses e tempo de emprego. O alvo y = 1 representa inadimplência. A divisão foi realizada com <b>default_rng(42).permutation</b>, sem sobreposição entre conjuntos.')
tab([['Conjunto','Amostras','% inadimplentes','Finalidade'],
     ['Treino','1.400',pct(D['proporcao_y1']['treino']),'Ajustar os pesos'],
     ['Validação','300',pct(D['proporcao_y1']['validacao']),'Ajustar hiperparâmetros'],
     ['Teste','300',pct(D['proporcao_y1']['teste']),'Avaliação final']],
    widths=[103,83,135,CW-321],font_size=8.0,row_pad=6)
para('Foi aplicado logaritmo natural apenas à renda, seguido de z-score com <b>média e desvio estimados exclusivamente no treino</b> e reutilizados na validação e no teste. O teste não orientou treino, escolha de limiar nem seleção do algoritmo genético.','small')
head('Validação preliminar: XOR')
figure('xor.png',width=290,height=225,captiontext='Figura 1. Fronteira não linear aprendida pela MLP com uma camada oculta.')
para('XOR não é linearmente separável: nenhuma reta classifica corretamente os quatro pontos. A camada oculta com ativação não linear compõe fronteiras de decisão, permitindo aprender os resultados 0, 1, 1 e 0; um Perceptron simples não consegue resolver o problema em todos os exemplos.','small')

# PAGE 3
newpage('02 / Redes neurais','MLP do zero e comparação')
para('A MLP tem <b>cinco entradas, uma camada oculta tanh e uma saída sigmoide</b>. Inicializa pesos aleatórios com escala proporcional à largura da camada, executa forward vetorizado, mede entropia cruzada binária (BCE) e calcula gradientes de W1, b1, W2 e b2 via regra da cadeia. O treinamento usa descida do gradiente em minibatches de até 128 exemplos, sem biblioteca de redes neurais.')
para('<b>Forward:</b> h = tanh(XW1 + b1), p = sigmoide(hW2 + b2). <b>Erro de saída:</b> dZ2 = (p - y)/m. <b>Retropropagação:</b> dZ1 = (dZ2 W2<super>T</super>) × (1 - h²), com atualização W ← W - taxa × gradiente. O cálculo da BCE usa logaddexp para estabilidade numérica.','small')
figure('perda_mlp.png',width=425,height=192,captiontext='Figura 2. Perda de treino e validação da configuração manual (16 neurônios, taxa 0,12, 140 épocas).')
head('Desempenho final no teste (limiar 0,5)')
rows=[['Modelo','Acurácia','Precisão','Recall','F1']]
for nome,m in D['metricas_teste_comparativo'].items():
    rows.append([nome,pct(m['acuracia']),pct(m['precisao']),pct(m['recall']),pct(m['f1'])])
tab(rows,widths=[170,85,84,75,CW-414],font_size=7.7,row_pad=7)
para('O Perceptron linear teve menor F1 que os demais. A regressão logística e a MLP do scikit-learn apresentaram resultados equivalentes neste conjunto. A MLP manual foi competitiva, mas sem superar esses dois baselines na configuração inicial. O scikit-learn foi empregado <b>somente</b> nos modelos comparativos autorizados pelo enunciado.','small')
para('<b>Custo dos erros.</b> Com y = 1 para inadimplente, falso negativo significa aprovar como adimplente um cliente que não pagará, implicando possível perda de capital. Falso positivo significa restringir crédito a alguém adimplente, gerando exclusão e perda de receita. Diminuir o limiar abaixo de 0,5 tende a elevar recall e reduzir falsos negativos, com possível aumento de falsos positivos; a política depende de custos e justiça definidos antes da implantação.','small')

# PAGE 4
newpage('03 / Lógica nebulosa','Definições e base de regras')
para('O controlador Mamdani recebe duas entradas normalizadas em [0,1]: <b>risco p</b> previsto pela MLP e <b>comprometimento de renda c</b> original da base. A saída em [0,100] é a porcentagem do limite máximo, sem representar o valor monetário diretamente. Cada variável apresenta termos baixo, médio e alto.')
head('Funções de pertinência')
para('Nas entradas: baixo = trapézio (0; 0; 0,20; 0,45), médio = triângulo (0,20; 0,50; 0,80), alto = trapézio (0,55; 0,80; 1; 1). Na saída: baixo = trapézio (0; 0; 15; 40), médio = triângulo (25; 50; 75), alto = trapézio (60; 85; 100; 100). As sobreposições favorecem transições graduais.','small')
figure('pertinencias.png',width=CW,height=176,captiontext='Figura 3. Funções triangulares e trapezoidais definidas para entradas e saída.')
head('Base de 9 regras SE–ENTÃO')
para('A lógica atribui crédito maior apenas para baixo risco e baixo comprometimento. Risco alto sempre implica limite baixo, enquanto maior comprometimento reduz a recomendação para um mesmo risco. Essas regras são <b>escolhas de política simulada</b>, não conclusões extraídas de dados de mercado.','small')
tab([['Risco \\ Compromet.','Baixo','Médio','Alto'],
     ['Baixo','ALTO','MÉDIO','BAIXO'],
     ['Médio','MÉDIO','MÉDIO','BAIXO'],
     ['Alto','BAIXO','BAIXO','BAIXO']],
    widths=[185,104,104,CW-393],font_size=8.5,row_pad=9)
para('<b>Mecanismo de inferência:</b> fuzzificação dos valores de p e c; ativação de cada regra por mínimo das pertinências; corte (mínimo) da função de saída correspondente; agregação pelo máximo; centroide calculado numericamente no universo de 0 a 100, com 1.001 pontos.','small')

# PAGE 5
newpage('04 / Controlador Mamdani','Inferência passo a passo')
D_f=D['exemplo_fuzzy_passo_a_passo']
para(f"Exemplo: cliente de teste <b>#{D['pipeline_cinco_clientes'][2]['id_teste']}</b>, com probabilidade de inadimplência <b>{pct(D_f['risco'])}</b> e comprometimento <b>{pct(D_f['comprometimento'])}</b>. O resultado da inferência é {fmt(D_f['centroide_percentual'],2)}% do limite máximo.")
head('1. Fuzzificação')
r=D_f['fuzzificacao_risco'];k=D_f['fuzzificacao_comprometimento']
tab([['Entrada','Baixo','Médio','Alto'],
     ['Risco p',fmt(r['baixo']),fmt(r['medio']),fmt(r['alto'])],
     ['Comprometimento c',fmt(k['baixo']),fmt(k['medio']),fmt(k['alto'])]],
    widths=[175,105,105,CW-385],font_size=8.4,row_pad=7)
head('2. Ativação, implicação e agregação')
regras=D_f['regras']
tab([['Regra','Antecedentes','Saída','Ativação α']]+[
      [str(i+1),item['risco']+' + '+item['comprometimento'],item['saida'],fmt(item['ativacao'],4)]
      for i,item in enumerate(regras)],
    widths=[55,205,105,CW-365],font_size=7.6,row_pad=2.2)
para('Por exemplo, R1: min(1,0000; 0,4443) = <b>0,4443</b> e R2: min(1,0000; 0,4631) = <b>0,4631</b>. Cada consequente é cortado na altura α da sua regra; a união das funções recortadas é feita por máximo em cada ponto do universo.','mini',gap=5)
head('3. Centroide da distribuição agregada')
para(f"Área = integral μ(z) dz ≈ <b>{fmt(D_f['area'],4)}</b>; primeiro momento = integral z·μ(z) dz ≈ <b>{fmt(D_f['momento'],4)}</b>. Centroide = momento / área = <b>{fmt(D_f['centroide_percentual'],2)}%</b>. Com teto didático de R$ 20.000, recomenda-se <b>{moeda(D['pipeline_cinco_clientes'][2]['limite_reais'])}</b>.",'small',gap=4)
# compact figure
figure('superficie_fuzzy.png',width=248,height=132,captiontext='Figura 4. Superfície: combinações de maior risco e comprometimento tendem a gerar limites menores.')

# PAGE 6
newpage('05 / Computação evolutiva','Algoritmo genético do zero')
para('O AG procura os hiperparâmetros que maximizam <b>F1 na validação</b>, sem olhar o teste. Cada cromossomo é uma tupla mista <b>(neurônios ocultos, taxa de aprendizado, épocas)</b>. Espaço de busca: 4–32 neurônios; taxa real 0,025–0,40; 70–220 épocas. As escolhas equilibram capacidade, rapidez e exploração do espaço de treinamento.')
head('Operadores evolutivos')
para('<b>População</b> de 10 indivíduos durante 10 gerações. <b>Seleção:</b> torneio de 3 candidatos. <b>Cruzamento:</b> uniforme nos genes inteiros e combinação aritmética na taxa. <b>Mutação:</b> probabilidade de 30% por gene, deslocamentos em neurônios/épocas e perturbação multiplicativa da taxa. <b>Elitismo:</b> preservação dos dois melhores. <b>Reparo:</b> limites e tipos válidos. Avaliações idênticas são armazenadas em cache.','small')
figure('convergencia_ag.png',width=445,height=206,captiontext='Figura 5. Evolução do melhor F1 e do F1 médio na população de cada geração.')
head('Melhor solução e generalização')
b=D['ag']['melhor'];mm=D['metricas_teste_comparativo']['MLP manual'];om=D['metricas_teste_otimizada']
tab([['Configuração','Neurônios','Taxa','Épocas','F1 teste'],
     ['Manual','16','0,1200','140',pct(mm['f1'])],
     ['AG',str(b['ocultos']),fmt(b['taxa'],4),str(b['epocas']),pct(om['f1'])]],
    widths=[130,95,95,80,CW-400],font_size=8.0,row_pad=7,highlight_last=True)
para(f"O melhor cromossomo alcançou <b>{pct(D['ag']['melhor_f1_validacao'])}</b> de F1 na validação, contra <b>{pct(D['f1_validacao_manual'])}</b> para a configuração manual. No teste, o ganho observado foi <b>{pct(om['f1']-mm['f1'])}</b> em pontos percentuais. A diferença é pequena em amostras de 300 casos e não prova superioridade estatística: o ajuste repetido ao conjunto de validação pode induzir sobreajuste. Isso exige confirmação em dados novos.",'small')

# PAGE 7
newpage('06 / Integração operacional','Pipeline aplicado a 5 clientes')
para('O pipeline recebe cinco atributos de um cliente, aplica o mesmo log e padronização do treino, estima o risco com a <b>MLP otimizada</b>, envia risco e comprometimento bruto ao Mamdani e obtém o percentual recomendado. Para exemplificar o valor em reais, adotou-se um <b>teto hipotético de R$ 20.000</b> igual para os cinco clientes.')
head('Exemplos do conjunto de teste')
rows=[['ID','Renda (R$)','Comp.','Atrasos','Risco','Limite %','Limite R$']]
for e in D['pipeline_cinco_clientes']:
    rows.append([str(e['id_teste']),f"{e['renda_reais']:.0f}",pct(e['comprometimento']),str(e['atrasos']),
                 pct(e['probabilidade_inadimplencia']),
                 f"{e['limite_percentual']:.1f}%".replace('.',','),
                 f"{e['limite_reais']:,.0f}".replace(',','.')])
tab(rows,widths=[43,96,76,66,68,71,CW-420],font_size=7.1,row_pad=7)
para('<b>Leitura:</b> o cliente #16, com risco estimado muito baixo, recebe 67,5% do teto, enquanto o cliente #240, cujo risco é mais elevado e tem maior comprometimento de renda, recebe 17,2%. As regras não definem aprovação/reprovação automática; definem apenas um percentual de limite, sujeito a políticas adicionais.','small')
head('Interpretação dos resultados')
figure('comparacao_modelos.png',width=410,height=172,captiontext='Figura 6. Comparação dos modelos no teste, incluindo precisão e recall.')
para(f"A MLP otimizada apresentou acurácia de <b>{pct(om['acuracia'])}</b>, precisão de <b>{pct(om['precisao'])}</b>, recall de <b>{pct(om['recall'])}</b> e F1 de <b>{pct(om['f1'])}</b>. Foram {om['FN']} falsos negativos e {om['FP']} falsos positivos no teste. Uma instituição real precisaria estimar custos dos dois erros, calibrar probabilidades e definir faixas de rejeição/revisão humana antes da concessão de crédito.",'small')

# PAGE 8
newpage('07 / Discussão e conclusão','Limitações, ética e transparência')
head('Limitações metodológicas')
para('Os registros foram gerados por uma função sintética, com padrões e ruído artificiais. O modelo pode explorar particularidades dessa geração e não necessariamente generalizar a clientes reais. A amostra de teste contém apenas 300 casos; uma diferença pontual em F1 não substitui análise de incerteza. Não foram realizados calibração de probabilidades, validação temporal, avaliação de deriva, teste externo ou análise de desempenho por grupos.','small')
para('A regra fuzzy considera somente risco e comprometimento e assume um teto fixo exemplificativo, sem capital disponível, política de crédito, custos regulatórios ou restrições contratuais. O AG consulta repetidamente os mesmos 300 exemplos de validação, o que aumenta o risco de escolher hiperparâmetros adaptados a esse conjunto. Em cenário real seria indicada validação repetida, monitoramento e auditoria independente.','small')
head('Riscos éticos e salvaguardas')
para('Decisões automatizadas de crédito podem gerar discriminação indireta, mesmo sem campos explicitamente sensíveis. Idade, renda, histórico de atraso e emprego podem atuar como proxies de vulnerabilidades sociais. Seriam necessárias avaliações de equidade, justificativas individualizadas, revisão humana em casos contestados, governança de dados pessoais e medidas de segurança e transparência. O experimento <b>não autoriza decisões financeiras sobre pessoas reais</b>.','small')
head('Conclusão')
para('A integração foi implementada com os três paradigmas exigidos: aprendizado supervisionado por backpropagation, raciocínio aproximado por Mamdani e busca evolutiva por AG. A MLP aprendeu XOR, o Mamdani produziu limites por regras auditáveis e o AG encontrou uma configuração com F1 maior no teste. O resultado é um protótipo didático reproduzível, não uma política validada de crédito. O próximo passo científico seria investigar calibração, estabilidade, custos de erro e equidade.','small')
head('Declaração de uso de IA generativa')
para('Foi utilizado <b>ChatGPT (OpenAI)</b> como apoio para estruturar a implementação, redigir explicações, organizar o relatório e produzir o material inicial de apresentação. O grupo deve executar, revisar e compreender o código, validar os resultados e informar quaisquer alterações de autoria. Essa declaração atende ao pedido expresso do enunciado e deve ser revisada pelos integrantes antes da entrega.','small')
head('Referências e materiais de apoio')
para('• Centro Universitário Padre Anchieta. <i>Trabalho Prático Integrador - CrediSmart</i>. Enunciado da disciplina Inteligência Artificial, 2026.','mini',gap=4)
para('• Código-fonte <i>main.py</i> e <i>credismart/</i>, arquivo <i>resultados.json</i> e gráficos gerados nesta execução. Dados sintéticos reproduzidos literalmente do enunciado.','mini',gap=4)
para('• NumPy, Matplotlib e scikit-learn: documentação das bibliotecas usadas para computação numérica, visualização e dois baselines comparativos.','mini',gap=4)

c.save()
print('Gerado:',OUT,'| paginas:',page)
