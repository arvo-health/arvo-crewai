## Autorizador: Refinamento UpStream Engenharia - Transcrição

### 00:00:00

   
Nathan Romeiro: Ih,  
Vinicius Paredes: Pronto.  
Nathan Romeiro: mano. Ih, bom, não vou mais  
Vinicius Paredes: Ó lá.  
Nathan Romeiro: responder.  
Vinicius Paredes: Então, o prestador ele é um ator externo ao sistema, né?  
Nathan Romeiro: Perfeito.  
Vinicius Paredes: Ele ele não tem acesso e mas só que ele  
Nathan Romeiro: Não,  
Vinicius Paredes: recebe notificação e espera um espera ações dele, não é isso?  
Nathan Romeiro: isso. Exato. Eh, sim. Em algum momento ele vai ter o módulo do prestador separado que não tá em nenhuma dessas versões que a gente fez hoje. O que que o prestador ele vai fazer? Ele sobe uma requisição igual o que o que a gente tá falando aqui com o Davi agora. Então ele sobe aquele pedido médico, mas ele tem esse, é quase como se fosse esse perfil standalone, né? Tipo assim, é um perfil que eu só subo requisição e eu recebo algumas notificações. Eh, o que a gente fez foi o módulo da operadora que tem necessariamente isso de subir uma solicitação e também fazer análise e dashboard. Eh, o prestador é um oito, é um é uma é uma, é só um módulo de subir que a gente ainda não desplugou, então a gente pode desconsiderar essa persona dessas versões, sabe?  
   
 

### 00:01:12

   
Vinicius Paredes: Tá, então ele ele vai sumir então prestador agora não vai entrar.  
Nathan Romeiro: Ele pode subir.  
Vinicius Paredes: Tá boa. Bom, eh, aí o que eu entendi ali que ele a gente tinha tem lá alguns lugares eh a menção de de integração com WhatsApp, com e-mail e seriam justamente essas notificações que iriam pro prestador, certo? Eh, isso também vai deixar de existir, então.  
Nathan Romeiro: Deixa existir. Pode deixar existir.  
Vinicius Paredes: Tá. Então, eh, integração com WhatsApp, e-mail, a gente não vai ter nessa versão.  
Nathan Romeiro: É, e a gente tá falando aqui M1, mas até M6,  
Vinicius Paredes: Beleza?  
Nathan Romeiro: isso aqui que a gente tá excluindo é até  
Victor Godinho de Lima: Ô,  
Nathan Romeiro: M6.  
Victor Godinho de Lima: agora uma pergunta, eh, até pegando um embalo aí que, enfim, que é um agent aí que gerou e ficou legal para caramba, viu, Natã? Depois dá uma olhada. Eh, ficou bem legal, quebrou lá por modos que nem o Vini mostrou. H, o certo agora, mas aí eu quero saber, enfim, onde que dá menos trabalho para todo mundo. Eh, mas o byook, ã, a gente teria que fazer essas mudanças do que a gente tá falando agora lá no documento principal e depois regerar aqui o impacto delas, porque aqui já tá com quebras e etc,  
   
 

### 00:02:28

   
Nathan Romeiro: Tá bom.  
Victor Godinho de Lima: pensando no que tava escrito lá. Eh, mas é uma pergunta, ô Vini, eh, você acha que é esse fluxo mesmo ou dá vai dar mais trabalho ainda? É mais fácil mudar no SRS direto?  
Vinicius Paredes: Então eu vou mudar no SRS paraa gente ter um contrato do que a gente vai entregar nesse nesse M1,  
Victor Godinho de Lima: Tá,  
Vinicius Paredes: certo?  
Victor Godinho de Lima: então não precisa alterar lá.  
Vinicius Paredes: Eh, eu acho que lá a gente não tem,  
Nathan Romeiro: Não Tem esse detalhe,  
Vinicius Paredes: tá?  
Nathan Romeiro: né? Os detalhes estão nas páginas,  
Vinicius Paredes: Eh, é ele ele ele não tá específico que há essa integração com o  
Nathan Romeiro: né?  
Victor Godinho de Lima: Bele,  
Vinicius Paredes: WhatsApp é no no M1 que você entrega, entendeu?  
Victor Godinho de Lima: tá bom.  
Vinicius Paredes: Boa.  
Willian Martinez: A questão da notificação inclui todos.  
Vinicius Paredes: Aí  
Willian Martinez: A gente não vai ter notificação até o final da entrega.  
Vinicius Paredes: não, a notificação,  
Nathan Romeiro: de M6 que é notificação pro  
Vinicius Paredes: tem uma notificação que é interna,  
Willian Martinez: É,  
Vinicius Paredes: tem um módulo de notificação que é isso que é que tem aqui,  
   
 

### 00:03:30

   
Willian Martinez: então aí não tem.  
Nathan Romeiro: usuário.  
Vinicius Paredes: tá? Tem um módulo aqui de  
Nathan Romeiro: É, tem uma que é a notificação e tem uma que é a comunicação.  
Vinicius Paredes: notificações.  
Nathan Romeiro: Isso que passou seria a comunicação entre prestadora e operadora. Isso não vai ter a notificação pro eh pra operadora. Aí é aquela notificaçãozinha lá de ah, chegou um novo pedido, tá?  
Vinicius Paredes: Boa. Aí tem aí justamente essa notificação, notification engine aqui. Eh, ele a gente não tinha nada, a gente não tem nada dela ainda, a gente já todo mundo sabe disso. Eh,  
Nathan Romeiro: M.  
Vinicius Paredes: mas só que um dos pontos que seriam desenvolvidos aqui seria um um web hook justamente para esses usuários que não têm acesso eh utilizarem um canal para para postar o as respostas, enfim. Então isso também vai deixar de existir.  
Nathan Romeiro: Patar. Ne,  
Vinicius Paredes: Boa.  
Nathan Romeiro: mat.  
Vinicius Paredes: Eh, ó, Davi.  
Davi Rojtenberg: Não, desculpa meu filho me dando tchau para ele vai para fechar.  
Vinicius Paredes: Ah, tá boa. Eh,  
Davi Rojtenberg: No.  
Vinicius Paredes: aí nisso aí eu entendo também então que esse módulo de pendência devolutiva deixa de existir, não?  
   
 

### 00:04:48

   
Vinicius Paredes: Porque eh o que que o que que é esse módulo de pendência devolutivo aqui? Mas aqui também tem um tem um ele ele é ele tem um ponto cross aqui. Ele faz ele ele é utilizado também com o conjunta médica. Eh  
Nathan Romeiro: que ele não deixa de existir, mas ele não tem a outra ponta que pluga, né? Porque esse aqui não é só a comunicação,  
Vinicius Paredes: Eh  
Nathan Romeiro: a pendência é meio que o workflow.  
Willian Martinez: Так.  
Nathan Romeiro: Ah, vou devolver isso aqui pro prestador. Eh, eu a gente já deveria prever qual que é a infraestrutura que eu vou usar aqui para eu salvar isso, para eu devolver, por exemplo, pro prestador. Mas, cara, eu não tenho ainda o onde ligar, né? Eu não tenho a tomada aqui para eu plugar, mas eu acho que essa estrutura aqui e é muito e não é comunicação por e-mail, não é nada disso, é imaginando que a gente vai salvar isso num canto e depois a gente vai chamar isso aqui para mostrar na tela do prestador lá que chegou uma pendência para ele, entendeu?  
Vinicius Paredes: Boa. E a e aí é justamente aqui o que que tá descrito aqui. Ele ele ele funciona meio que como uma máquina de status, uma máquina de estatus de de de pendência,  
   
 

### 00:05:54

   
Nathan Romeiro: Isso.  
Vinicius Paredes: né? Então a gente a gente vai vou preciso da ação do do  
Nathan Romeiro: Uhum.  
Vinicius Paredes: prestador lá externo. Beleza, eu vou registrar que a gente tá esperando a ação do prestador externo. Eh, ele respondeu, a gente não chegou nesse ponto ainda, mas aí tem um status, um status definido para paraa resposta, pra resposta. Ele tem o tempo para fazer essa resposta também, é o deadline aqui. Então isso tudo vai ficar registrado também, tá? Eh, o que a gente não vai ter é justamente a resposta, pelo que eu entendi, né? Eh, boa.  
Nathan Romeiro: Sì.  
Vinicius Paredes: E aí tem toda a questão de exibição aqui do do desses desses substatus, né? Falou que eu a solicitação já tem um status. Isso aqui seria um substatus. Tem questão também de de registro de log para que a gente tenha uma uma possibilidade de auditoria. tudo tudo que acontece, ele monta um um audit log ali para ser servir meio que um como um timeline do dos eventos que acontecem na sua licitação. E aí aqui esse processo de retorno do prestador eh eu aí isso aqui eu acho que vai é um requisito que vai sumir, né? E aí ele ele coloca aqui recebeu retorno viab que aí eu falei que que deixou de fazer sentido e atualiza os status aqui.  
   
 

### 00:07:26

   
Vinicius Paredes: M.  
Nathan Romeiro: É, não vai ter esse retorno ainda, mas já daria para deixar isso previsto, sabe? Quando a gente for fazer essa o sistema do prestador, ele já ter isso meio que configurado eh para receber retorno ou tira e só faz isso depois.É, tipo, a gente não vai ter como testar isso. Acho que esse é o ponto,  
Vinicius Paredes: Tá boa.  
Nathan Romeiro: né?  
Vinicius Paredes: Beleza. É, dando dando partindo do pressuposto que ele faz somente uma atualização de de alguns campos eh e que o processamento é é é basicamente um update e eu vou e o webhook seria um um end point a mais no na minha PI. Eh, OK. Aí lá na frente a gente deferia definiria contratos, os meios de de acionamento, enfim. Eh, aí prazos, eh, aí prazo, eh, eu não sei se tem algo fixo ou precisa ser algo configurável por tenet, por atopo, enfim, isso eu não consegui identificar eh nenhuma definição. Eu sei que tem, eu sei que a gente tem um prazo de SLA da solicitação,  
Willian Martinez: Kalau  
Vinicius Paredes: mas a gente tem um prazo de de tipo assim definido já de resposta do operador, do prestador, no caso.  
Nathan Romeiro: p***, não.  
   
 

### 00:09:11

   
Vinicius Paredes: Tá. Então vou deixar isso aberto também. Beleza. Boa. Eh, segundo ponto aqui, junta médica. O junto médica, ele é bem parecido ali com a notifica com com a notificação do do prestador.  
Nathan Romeiro: é um estado, né?  
Vinicius Paredes: É uma máquina de estados também. Eh, a diferença é que ele tem campos aqui que são, ele tem regras aqui de até de string que eu vi ali, que não deve ser a junta aprovou, junta negou, é sempre algo mais genérico assim, né? E e aí tem o campo, tem os tem o formulário de de envio paraa junta e que tem alguns campos que são obrigatórios, né? Eh, que é a razão porque que tá indo paraa junta médica e justificativa. Certo? Aí o que eu fiquei na dúvida aqui,  
Nathan Romeiro: Так.  
Vinicius Paredes: Natã, o que eu não consegui ver ali, foi que a gente tem o caminho de ida e a gente tem um caminho de volta, mas só que aí eu acho que sen já até respondeu lá pelo pelo pelo prestador. A gente não tem o meio de de ida. Como é que ele vai responder isso aí? Entendeu? Tipo, eh, eu tenho aqui que, ó, esse aqui, esses campos são obrigatórios para enviar pro para junta médica, certo?  
   
 

### 00:10:50

   
Vinicius Paredes: E quando ele responder,  
Nathan Romeiro: M.  
Vinicius Paredes: ó, quando ele ele tiver um parecer, ou seja, quando ele responder, vai acontecer isso aqui. Eu vou atualizar isso, vai mudar, vai ser adicionado ao ao audit log lá da solicitação para para que conte registro que fulano respondeu tal hora. Eh, mas só que eu não eu não tenho o que que eu vou esperar dessa resposta, entendeu? Vai ser só OK, não OK, vai ter um vai ter um texto,  
Nathan Romeiro: Cara,  
Vinicius Paredes: enfim.  
Nathan Romeiro: o que o que o que eu acho que isso diferencia do prestador? O prestador ele é autocido no nosso sistema, né? Então a gente, o nosso sistema vai receber a própria resposta,  
Vinicius Paredes: Угуm.  
Nathan Romeiro: a gente vai mudar, porque o prestador vai usar o nosso sistema para colocar lá eh o retorno dele na junta médica eventualmente, e eu acho que isso acontece na maioria dos casos, eventualmente não, eh na maioria dos casos, isso aqui é feito fora de qualquer sistema, ou pode ser por e-mail, ou pode ser por um sistema de junta médica específico, né, que a empresa contrata por fora, mas isso aqui é não é autoconto. Então o que vai retornar não vai ser um web hook, uma chamada.  
   
 

### 00:12:06

   
Nathan Romeiro: Provavelmente o operador vai ter que adicionar o essa informação que deve vir com um laudo, né, que esse é um laudo em texto e deve vir, sei lá, um um PDF, sabe? Eh, mas aí a gente manda para ajudar. Esse é um status que ele é necessário, mas diferente do que é o do prestador que, tipo, tem um workflow, aquele é um workflow meio um ponto final. E depois a gente recebe essa informação e aí provavelmente quem vai subir essa informação é o operador que ele sobe lá, fala: "Ah, a retorno da junta médica é esse, é uma caixa de texto e pode ter um anexo também que é o PDF do da junta médica, entendeu?" Então,  
Vinicius Paredes: Entendi. Fala aí, Al.  
Nathan Romeiro: acho que simplifica aqui nesse caso.  
Alexander Gonzalez: Uma dúvida que eu lembro quando a gente falou com Atena que  
Nathan Romeiro: Pode falar, Alex.  
Alexander Gonzalez: eles eles saem do sistema, entraram no outro site, mandam e em algum momento eles recebem tipo um e-mail, mas tá tudo. Mas esse padrão de Atena é padrão do mercado ou é que Atena faz desse jeito assim manual? Porque talvez tenha outro ser automático e para fazer algo parecido.  
Nathan Romeiro: Não, cara, eu acho que nem nenhuma vai ser automática assim, porque é o a a junta médica são médicos que você contrata por fora, eh, e ele não tem acesso ao seu sistema, então ele não vai, você não vai treinar o médico pro fora no ERP, ele vai receber um laudo lá.  
   
 

### 00:13:26

   
Nathan Romeiro: lá o ponto de vista e vai escrever o ponto de vista dele. Eh, então, pelo que eu tô entendendo,  
Vinicius Paredes: M.  
Nathan Romeiro: é é padrão de mercado fazer fazer isso por fora, ainda que Atena tem um outro sistema, né, que usa que lembra que ele falou que dispara tal,  
Alexander Gonzalez: Ele falaram errou tropa.  
Nathan Romeiro: mas o é,  
Alexander Gonzalez: externo que le false Isso.  
Nathan Romeiro: mas a resposta é por e-mail, sei lá.  
Vinicius Paredes: Tá aí. fala aqui do do de como fica no histórico pós decisão da junta. E aí é um ponto aqui, cara, que eu acho que é o que mais que eu mais tentei prestar atenção para entender, para eu não ter não deixar passar nada assim, porque eu acho que é um ponto crítico é justamente o sea, inclusive tem um outro módulo exclusivo para ele lá. Eh, ele, o SLA, ele é ele é como se fosse uma bala disparada, né? Ele começou ali, não, ele não, o tempo que tá rolando, ele não, ele não para mais, exceto nesse caso da junta médica. É  
Nathan Romeiro: você pode adicionar, né, um um adicionar três dias úteis,  
Vinicius Paredes: isso.  
Nathan Romeiro: cara. Eu eu simplificaria, não é que ele para de contar, até porque se médica esquecer que que você faz, né?  
   
 

### 00:14:49

   
Nathan Romeiro: Eh, eh, você adiciona três dias úteis no período máximo de SLA determinada. Eh, cara,  
Vinicius Paredes: Então ela é como se ela fosse prorrogada por por um período.  
Nathan Romeiro: eu chum prorrogado três dias.  
Vinicius Paredes: Boa. Tá. Tá.  
Nathan Romeiro: Isso.  
Vinicius Paredes: Aí aí aí. Isso aqui também, ó, esses múltiplos níveis algo que eu fiquei eu fiquei em dúvida. Eu sei que tem junta médica, eh, do município, estado, enfim, tem vários níveis aí de junta médica. É isso aqui que a gente tá falando, eu poderia, pode ser que, vamos supor, uma junta médica do município mande mande pro para outra junta médica do estado,  
Nathan Romeiro: É, na verdade que tem,  
Vinicius Paredes: ou eu tô falando m****.  
Nathan Romeiro: eu, cara, eu não sei se de município de estado, mas é a junta médica é um, é um grupo de profissionais que vai analisar seu caso.  
Vinicius Paredes: É, é um conselho ali,  
Nathan Romeiro: E aí é um conselho isso.  
Vinicius Paredes: né, de médicos que tá boa,  
Nathan Romeiro: E  
Vinicius Paredes: mas eu posso ter essa escalation assim de para outro nível de junta ou para outro grupo de  
Nathan Romeiro: e  
Vinicius Paredes: junta, tipo,  
Nathan Romeiro: não acho que uma vez que o analista manda pra junta médica,  
   
 

### 00:16:01

   
Vinicius Paredes: não conseg  
Nathan Romeiro: a junta médica pode ter um uma próxima junta de desempate, sabe? Tipo, ah, eu eu tenho uma opinião, mandei para uma junta médica porque eu não tô muito convicto. Aí se ele, esse cara também não tá muito convicto, ele pode mandar para outro, pode mandar. Eu acho que a gente tem que dentro do sistema, a gente deveria simplificar e falar: "Cara, junta médica, é junta médica, independente de quantas escalas isso vai ter.  
Vinicius Paredes: É, é isso que eu que eu queria entender a nível de sistema, quando eu receber um parecer da junta médica, eu tenho a possibilidade de parecer esse que eles eles enviaram para outra junta médica e eu vou precisar também ficar aguardando isso aí. Isso envolve até aumentar de novo os três dias lá do SLA ou só não só  
Nathan Romeiro: Não, não, não. Acho que não.  
Vinicius Paredes: esperar aqui a junta médica e não preciso saber o que tá acontecendo para  
Nathan Romeiro: Não é f***-se.  
Vinicius Paredes: lá.  
Nathan Romeiro: Pode ser 15 juntas médicas. Os caras fizeram, mas eles vão devolver em três dias e vai ser o relatório é o mesmo,  
Vinicius Paredes: Bom,  
Nathan Romeiro: sabe?  
Vinicius Paredes: então esses múltiplos níveis aqui, esquece, né?  
   
 

### 00:17:01

   
Vinicius Paredes: Boa.  
Nathan Romeiro: Esquece.  
Willian Martinez: M.  
Vinicius Paredes: Eh, aí tem o módulo de notificações que eu acho que já tá bem alinhado, que a gente já tinha conversado antes. Eh, tem aí eu peço que vocês deem uma olhada também no no em cada tipo de notificação aqui, tá? Eh, aí a gente tem um tem um um ponto de de atenção aqui que são mensagens eh para cada notificação. Eh, tinha conversado até sobre os níveis, né, de notificação, se se era restrito ao usuário, é, se era para para envio para para todo um grupo de  
Nathan Romeiro: Você  
Vinicius Paredes: usuários ou então a nível de tenet, enfim. Eh,  
Nathan Romeiro: tá falando das notificações que aparecem ali na tela, né?  
Vinicius Paredes: exato.  
Victor Godinho de Lima: Só  
Vinicius Paredes: a notificação que aparece lá na na no nosso no próprio sistema do autorizador.  
Nathan Romeiro: Cara,  
Vinicius Paredes: M.  
Victor Godinho de Lima: você.  
Nathan Romeiro: notificação é f***, né? Porque precisamos definir quem é o usuário, qual é a regra, qual é a régua, eh, qual que é o qual que é o trigger, qual que é o a consequência.  
Willian Martinez: M.  
Victor Godinho de Lima: E aí, pegando um gatilho nisso aí, ô Alex, te fazer uma pergunta.  
   
 

### 00:18:22

   
Victor Godinho de Lima: Eh,  
Vinicius Paredes: Ja.  
Victor Godinho de Lima: DS já tá retornando lá na análise da solicitação  
Vinicius Paredes: Ja.  
Victor Godinho de Lima: eh de autorização, aqueles insites ali positivo, warning.  
Willian Martinez: M.  
Victor Godinho de Lima: Vocês já estão retornando aquilo?  
Alexander Gonzalez: Agora ele retorna só se está tem três estátu análises humana, fa aprovado e reprovado. Acho que não não retorna ainda. Você fala que retorna a resposta por cada gente com todas as regras.  
Victor Godinho de Lima: Eh, não é aquele, acho que é mais fácil mostrando depois uma parte da tela, eh, mas é aqueles, ã, aquela aqueles aqueles feedbacks paraa pessoa que vai aprovar a autorização do tipo,  
Vinicius Paredes: Eu  
Victor Godinho de Lima: olha, a gente checou isso, tá, tá OK, isso aqui tá esquisito, eu já fez fez múltiplas requisições nos últimos três meses. Eh,  
Alexander Gonzalez: Ah, no, ainda não volta histórico.  
Victor Godinho de Lima: aqui.  
Alexander Gonzalez: Esas valcies detalh  
Vinicius Paredes: vou precisar de 2 minutos só para falar pro cara que chegou fazer um serviço o que que é para fazer. 2 minutos já volto.  
Victor Godinho de Lima: Tá,  
Nathan Romeiro: Ja.  
Alexander Gonzalez: deber  
Victor Godinho de Lima: tá.  
   
 

### 00:19:36

   
Victor Godinho de Lima: Mas já tem o formato de como é que vai ser a resposta de vocês,  
Alexander Gonzalez: não teria que ver comenso, tá? Se ele já pensou isso, mas por enquanto  
Victor Godinho de Lima: tá?  
Alexander Gonzalez: não,  
Victor Godinho de Lima: Porque a gente tá entrando nessa parte exatamente agora. Eh,  
Alexander Gonzalez: mas vamos anotar para ver aqui se ele pensou e se não eu defino.  
Victor Godinho de Lima: é, eh, pelo menos definiu o Jason, como é que vai ser ali o modelo para que aí a gente já estrutura aqui por hora vai estar vazio e depois não, mas aí já a gente já tá com contrato.  
Willian Martinez: Isso, isso também entra aqueles toast message. Essa é a notificação, certo? Que são aquelas mensagens que ele aparece no cantinho.  
Victor Godinho de Lima: Eh, o V tava falando das notificações que aparecam no canto e eu tava falando daquelas mensagens que são positivas ou warning. que é lá no detalhe que a pessoa vai aprovar ou não uma solicitação,  
Willian Martinez: Uhum.  
Victor Godinho de Lima: que é a análise da IA,  
Willian Martinez: Uhum.  
Victor Godinho de Lima: é um um idgat que fica ali em cima na direita.  
Willian Martinez: Sim. E o e aquele sininho que dá essas notificações  
Vinicius Paredes: É,  
   
 

### 00:20:54

   
Victor Godinho de Lima: Esse é o que eu tava É,  
Vinicius Paredes: esse é notificações.  
Willian Martinez: ele?  
Victor Godinho de Lima: sabe o que o tava falando.  
Willian Martinez: Tá beleza. Mas esse cara toda toast message também vai para lá ou a gente vai ter toast message separados para algum algum problema, algum erro, alguma coisa assim? Inclusive, a gente tava falando sobre isso. A gente meio fez, o Davi fez a versão RPEF, né? Se a gente não tem algumas coisas casos de erro na no meio do processo. Então, talvez depois a gente levantar essas coisas.  
Vinicius Paredes: Eh, então aí, aí É outro ponto. Foi bom eu lembrar disso aí. Eh, eu mapei alguns alguns pontos aqui de que são triggers de de notificações, tá? Eh, mas eh eu não sei se tem algum outro que que ficou de fora e aí era bom também eh dar uma uma lida aqui, ver se precisa algum algum não faz sentido ou se precisa incluir algum.  
Willian Martinez: Ne. Uhum.  
Nathan Romeiro: Tá  
Vinicius Paredes: Beleza.  
Nathan Romeiro: bom.  
Willian Martinez: E você vai ter que passar uma por uma aí até até colocar o título para quem que vai mesmo ou não.  
Victor Godinho de Lima: Так.  
Willian Martinez: Vai vai ter que ser classificando uma a uma  
   
 

### 00:22:06

   
Vinicius Paredes: É definir para quem que vai,  
Willian Martinez: mesmo.  
Vinicius Paredes: para qual mensagem que vai, que aqui é só o evento, né?  
Nathan Romeiro: Uhum.  
Willian Martinez: Uhum.  
Vinicius Paredes: Beleza.  
Nathan Romeiro: Tá bom. Tá essa essa essa tesca aí para mim que eu faço  
Vinicius Paredes: É.  
Nathan Romeiro: aí.  
Vinicius Paredes: Aí isso aqui vai sumir também, né? Que é o notificação outbound para para prestador a gente não vai ter,  
Nathan Romeiro: Isso, isso.  
Vinicius Paredes: tá? Depois eu tiro, tá? Aí, isso aqui, ó, a gente volta lá pro pro pra discussão do da atualização em tempo real via socket, o SSE, mas isso aí é algo mais técnico, vou deixar lá pra frente. Eh, módulo sete, permissões de controle de perfil. A gente já tem algo implementado nesse sentido, né? A gente só tem ali o Alf Zero implementado. Eu acho que o que a a a o objetivo aqui é é chegar numa versão final,  
Nathan Romeiro: É mais configurar,  
Vinicius Paredes: né? Isso.  
Nathan Romeiro: né?  
Vinicius Paredes: Chegar numa versão final e boa. E e montar também o dashboard, né? Não, das não, uma interface para gerenciar isso, porque hoje a gente tá precisando eh entrar lá no office zero para para atribuir, para criar usuário, atribuir permissão, enfim.  
   
 

### 00:23:35

   
Vinicius Paredes: Controle de concorrência. Ah, isso aqui é uma coisa, cara, isso aqui vai ser um ponto interessante assim. Eh, o que que é o o operator lock aqui?  
Willian Martinez: อ  
Vinicius Paredes: Ele a gente tem a o precedente lá de que quando uma uma solicitação tá sendo utilizada, analisada, no caso, eh ela fica eh travada, fica, eh é travada, né? travada por para caso um segundo um segundo  
Willian Martinez: M.  
Vinicius Paredes: usuário entre naquela solicitação,  
Victor Godinho de Lima: M.  
Vinicius Paredes: ele não consiga operar aquilo ali, não consiga aprovar, rejeitar, enfim. Eh, então,  
Nathan Romeiro: Угуm.  
Vinicius Paredes: qual foi a ideia aqui de, p****, eu aprovei e o cara vai lá e nega qual é o que tá valendo, entendeu? Eh, e aí tem operator lock.  
Nathan Romeiro: Угу.  
Vinicius Paredes: A ideia é na hora que que a o primeiro usuário entrar, ele registra esse esse travamento e ele tem o TTL ali para que para que ele fique travado. Eu coloquei aqui 15 minutos. Eh, e são dois critérios, no caso, 5 15 minutos e um rest bit, que aí a gente pode definir a cada 5 minutos.  
   
 

### 00:25:05

   
Vinicius Paredes: Tá, que pode acontecer dele não sair também, né? Ele entrou ali, cara, deixou a página aberta. Eh, como é que eu que eu sei que ele tá ele tá com a página aberta ali? Entendeu? Não é só eu registrar o o lock na hora que ele acessa a solicitação, mas se ele acessar, por exemplo, e depois fechar o navegador, ele vai ficar travado para sempre, né? E aí,  
Nathan Romeiro: Entendo.  
Vinicius Paredes: essa é a ideia do RBIT para que na página lá de de de solicitação, de detalhe da solicitação, ele eu fica enviando. Olha, esse cara tá analisando ainda. Enquanto ele tiver analisando, ele tá ele tá travado para que nenhum outro consiga consiga atuar, certo? E aí tem um segundo ponto aqui que é um que é o unck. ock seria forçar essa essa essa essa essa essa destrava aí, mas com permissão restrita a a a certos tipos de usuários, tipo eh administrador, enfim. OK, funciona. Dá para funcionar desse jeito ou não  
Nathan Romeiro: Gostei. Dá, dá para funcionar sim.  
Vinicius Paredes: precisa disso?  
Nathan Romeiro: Ah, cara, eu acho que isso vai ser importante.  
   
 

### 00:26:30

   
Nathan Romeiro: É porque quando alguém pega para ver, tá na fila, alguém pega para fazer. Aí isso tem que ficar de alguma de algum jeito. Você tem que ficar num pessoa, uma segunda pessoa pode fazer,  
Vinicius Paredes: Tem que ser visível,  
Nathan Romeiro: tá ligado?  
Vinicius Paredes: né?  
Nathan Romeiro: É, tem que ser visível. Tipo assim, a gente tem que bloquear essa parada e pra pessoa pra pessoa finalizar. Eh, e aí depois que ela finaliza fica destravada, né? Tipo assim, qualquer um pode ir lá olhar, mas aí entra no no caminho normal.  
Vinicius Paredes: Boa.  
Nathan Romeiro: Eh, mas eu acho que é importante  
Vinicius Paredes: Beleza. Tá aí.  
Nathan Romeiro: isso.  
Vinicius Paredes: SL. Esse aqui que é o acho que é o ponto que a gente mais precja atenção. Eh, vamos lá. Se ele acho que todo mundo sabe o que que é, né? Aí tem alguns pontos,  
Nathan Romeiro: Mhm.  
Vinicius Paredes: cara, eh, que eu vi que tem eh tem a  
Willian Martinez: Olha  
Vinicius Paredes: a necessidade de de de pausar esse esse SLA. Eh, o único que eu vi assim efetivamente, que é a regra de de assim bem definida é da junta médica, né?  
   
 

### 00:28:00

   
Nathan Romeiro: M. Ah, é a única que tem,  
Vinicius Paredes: Mas caso é porque eu vi que tinha a possibilidade do do  
Nathan Romeiro: é a única que pode mudar. É,  
Vinicius Paredes: do gestor para para usar esse SLA, tipo, administrativamente, entendeu? Isso. Então eu entendi errado. Não  
Nathan Romeiro: cara. Não, não, assim, pode simplificar porque o beneficiário tá c****** assim, né? Tipo, o beneficiário,  
Vinicius Paredes: existe.  
Nathan Romeiro: ele tem a NS fala que precisa dar uma resposta em cinco dias, ele quer a resposta em cinco dias, aí demorou oito, aí ele vai bater lá na ES e vai falar: "Ó, os caras não me responderam ainda". Aí a operadora vai justificar, fala: "Não, mas isso aqui é porque eu mandei para uma junta médica, tenho mais três dias". Cara, é a única coisa. Eh, o SLA ele é estático, ele é por evento. A gente é assim, a gente tem que simplificar o máximo aqui, sabe?  
Vinicius Paredes: Ah, bom.  
Nathan Romeiro: É.  
Vinicius Paredes: Então, então, cara, então que bom que eu tinha, eu tinha visto que tinha a possibilidade do do operador pausar isso aí quando ele ele quisesse.  
   
 

### 00:28:55

   
Vinicius Paredes: Aí eu comecei a pensar, cara, aí a gente tá ferindo,  
Nathan Romeiro: Como é que vai fazer essa p****?  
Vinicius Paredes: é, como a gente tá ferindo uma um pressuposto do SLA, né?  
Nathan Romeiro: É, não, não, cara.  
Vinicius Paredes: Eh,  
Nathan Romeiro: SL é a hora da entrada mais X tempos definido numa regra que é uma tabela que a gente vai consultar e falar: "Ah, para esse evento aqui são 10 dias, é dado de entrada mais 10 dias.  
Vinicius Paredes: então beleza. Aí porque aí que eu tinha eu tinha tinha colocado uma proposta de relógio duplo aqui, o SLA que é que é escrito em pedra e o outro que é meio que um interno administrativo. Enfim, mas eu tirei, eu vou tirar isso. Então fala, ô Davi, pode escrever os os SL. Ah,  
Nathan Romeiro: Ah, tá.  
Vinicius Paredes: falando para ele diminuir  
Nathan Romeiro: O que o Davi tá falando é é vou dar um SL a um dia menos.  
Davi Rojtenberg: Porque você tem você tem os SL que são pré-definidos pela pelas regras da NS, mas as operadoras geralmente modificam. Ela internamente ela fala assim, ó, estão falando que é 21 dias para esse exame,  
Nathan Romeiro: Sì.  
   
 

### 00:29:57

   
Davi Rojtenberg: mas internamente aqui são 10. A gente precisa disso resolvido em 10. Então eles pressionam mais o autorizador nesses casos.  
Nathan Romeiro: Pode ser.  
Davi Rojtenberg: A gente vai ter que inventar uma de costumes aí.  
Vinicius Paredes: Tá aí. Qual seria a proposta? a gente fazer um SL duplo,  
Nathan Romeiro: Não, não.  
Vinicius Paredes: SLA configurável ou a gente vai nessa e depois a gente evolui.  
Nathan Romeiro: Acho que é um único.  
Vinicius Paredes: Pode ser  
Nathan Romeiro: É, pode ser. Qualquer coisa a gente vê, ah, pô, tem uma outra empresa que quer diferente, a gente faz por tenant, sabe?  
Vinicius Paredes: boa.  
Nathan Romeiro: uma variável ali.  
Victor Godinho de Lima: Eu também acho que a gente vai acabar configurando por  
Nathan Romeiro: Ah,  
Victor Godinho de Lima: Tet.  
Nathan Romeiro: mas eu acho que é esse é o máximo de customização que deveria dar, sabe?  
Vinicius Paredes: Boa. Eh, aqui checklist de de catálogo TEA. Aí, isso aqui é aquele checklist lá que a gente tinha discutido da da do retorno da IA, tá? Eh, tem aí são aquelas  
Nathan Romeiro: Uhum.  
Vinicius Paredes: definições. Eh, ele ele catalogou aqui 32 itens, mas ele não identificou uma, por isso que ele colocou um ponto de de atenção aqui.  
   
 

### 00:31:12

   
Nathan Romeiro: Угуm.  
Vinicius Paredes: Eh, a gente já tem isso catalogado, tudo bem definido, o vai precisar de mudança. Eh, a gente definiu também a questão de severidade, né? Eh, a gente chegou, não, a gente chegou a combinar, mas não ficou nada definido. Eh, questão de severidade para que elas sejam exibidas e outra, umas sejam exibidas, outras não. Enfim,  
Nathan Romeiro: Uhum.  
Vinicius Paredes: eh, a gente já tem isso aqui definido.  
Nathan Romeiro: Acho que definido sim.  
Vinicius Paredes: M.  
Nathan Romeiro: Em nesse nível de detalhe que a gente precisa definir por severidade, né? Qual que é a regra? Eh, isso aí não. Bota para mim, eu te entrego até sexta. Pode ser.  
Vinicius Paredes: Ó, aí já tá gravando, tá?  
Nathan Romeiro: Tá bom. Geminai,  
Alexander Gonzalez: Uma dúvida aí,  
Nathan Romeiro: já tem duas tesques aí para mim.  
Alexander Gonzalez: esse checklist da IA são a resposta dos agentes?  
Vinicius Paredes: Isso é isso. Isso.  
Nathan Romeiro: É o jeito que a gente mostra. Depois o Davi mostra para você, eh, Alex, mas é o jeito que a gente são todas as validações que a gente faz,  
   
 

### 00:32:28

   
Vinicius Paredes: Isso.  
Nathan Romeiro: é uma validação exaustiva. Então, não é um retorno da IA sobre aquele item específico. Pode ser, a gente pode frame dessa maneira, mas ou a gente pode deixar como sendo, cara, um checklist exaustível e a gente faz um pós-processamento do retorno da EA para inferir esses pontos que a gente avalia, tá? Eu eu tenho,  
Vinicius Paredes: É isso aqui, ó.  
Nathan Romeiro: é isso aí, Alex, eu tenho duas reuniões ainda.  
Vinicius Paredes: Fala.  
Nathan Romeiro: Eu posso sair, depois eu volto. Podemos, a gente pode pausar aqui ou vocês continuam e aí podem Sim.  
Vinicius Paredes: Não, cara, o restante aqui já é mais pro nosso lado. Assim, eu vou confirmar algumas coisas com com o Davi com relação a essa interface do usuário, mas o resto aqui back end já é nosso e se surge alguma dúvida eu eu posto o comentário aqui te marcando. Pode ser?  
Nathan Romeiro: Beleza.  
Alexander Gonzalez: uma dúvida aí antes de Nat que  
Nathan Romeiro: Eh,  
Alexander Gonzalez: dá volte todos a gente tipo positivo, negativo ou que dieron  
Nathan Romeiro: aí tem uma ló,  
Alexander Gonzalez: ruim?  
Nathan Romeiro: acho que positivo e negativo a gente tem que saber o positivo o que deu positivo e o negativo a gente tem que saber o que negativo.  
   
 

### 00:33:45

   
Nathan Romeiro: A gente pode ter uma resposta só do negativo e inferir que o que não veio é positivo, mas a gente tem que ter um ponto de vista de todos aqueles pontos.  
Alexander Gonzalez: Por isso, então eu tenho que retornar de 10, eu tenho que retornar resposta de 10. falando e tá OK ou tá ruim assim ou posso retornar só cinco que dieram ruim e os outros cinco não porque  
Nathan Romeiro: É, acho que pode retornar só os que deram ruim e a gente infere que os que não deram ruim deram bom,  
Alexander Gonzalez: No.  
Nathan Romeiro: sabe? Eu acho que existe uma camada aqui de pós-processamento da inteligência que a gente vai precisar construir e pensar direitinho nela. Eh, mas pode ser isso, tipo assim, ah, tudo que se eu se não me mandou nada é porque tá tudo bom e eu valido tudo, entendeu?  
Alexander Gonzalez: Porque aí depende como v o retorno. Acho que só alinhar com que falou Godinho se voltar  
Nathan Romeiro: Eu preciso lá.  
Vinicius Paredes: Aí, só alinhamento agora aqui de de inteligência com engenharia. Eh, esse isso aqui é um é um pelúdio completo que tá ligado a um tipo que é aqui ao laudo de vigência, por exemplo, ele vai ter o texto, status, enfim. Eh, que que vocês acham que seria o melhor?  
   
 

### 00:35:12

   
Vinicius Paredes: a gente retornar de de lá de inteligência o objeto completo ou retorna somente o tipo aqui o o ID do item, no caso. E aí no na engenharia a gente pula o restante do do do objeto.  
Alexander Gonzalez: pensando porque o que a gente retorna agora são por cada procedimento a resposta de cada certo  
Vinicius Paredes: É porque isso aqui também pode acontecer de, ah, não quero mudar esse texto aqui. É onde fica onde ficaria mais fácil de mudar, entendeu? Pensando nisso,  
Alexander Gonzalez: Mas pelo menos esse texto seria um motivo glosa ou  
Vinicius Paredes: olha aqui, ó,  
Alexander Gonzalez: seria  
Vinicius Paredes: esse texto aqui, esse, entendeu?  
Alexander Gonzalez: certo, mas é que se normalmente nos agentes, o que a gente coloca de texto é o motivo glossa, que é diretamente o que está no na ns, sabe? Código 1325 profissional tá ou a gente precisa mudar para um texto assim mais bonito ou  
Victor Godinho de Lima: teria que mudar para um texto assim mais bonito. Eh, vocês mandariam essa lista de textos.  
Alexander Gonzalez: entend?  
Victor Godinho de Lima: Esse aí é o cara que eu tava comentando lá do dos insightes de positivo, warning, vocês tornariam essa lista de feedbacks da IA, tipo  
Alexander Gonzalez: Por exemplo, agora se ele valida idade, ele volta código tal procedimento for idade,  
   
 

### 00:37:05

   
Victor Godinho de Lima: assim,  
Alexander Gonzalez: fora da permitida, tá? Ele volta literalmente o motivo do do da glossa, entende?  
Victor Godinho de Lima: por exemplo, isso aí são só exemplos exemplos de frases. A ideia é que aí vocês iriam mapear pontos que valem a pena serem retornados como  
Alexander Gonzalez: Entendi.  
Victor Godinho de Lima: pontos positivos e de atenção, enfim, com xizinho,  
Alexander Gonzalez: Eu acho que aí vale a  
Vinicius Paredes: Mas aí,  
Willian Martinez: Угуm.  
Vinicius Paredes: Godinho,  
Victor Godinho de Lima: enfim.  
Alexander Gonzalez: pena.  
Vinicius Paredes: só só ver se eh a resposta da IA, né?  
Victor Godinho de Lima: Uhum.  
Vinicius Paredes: Eh, isso aí é aqui, não é? Não é o ponto, é o o parecer. O checklist é o que ele tem que ver, não é isso? Para resolver, não é isso? Se eu tô errado.  
Victor Godinho de Lima: Eh,  
Vinicius Paredes: E aí, tipo assim,  
Victor Godinho de Lima: eu  
Vinicius Paredes: eh, no caso do do Sid lá que tu tu deu o exemplo, eh, a o texto aqui do do checklist seria se incompatível.  
Victor Godinho de Lima: hum Hum. Então,  
Vinicius Paredes: E aí ele colocaria o descrição aqui em cima no ponto de vista da IA,  
   
 

### 00:38:19

   
Victor Godinho de Lima: mas como é que você Então,  
Vinicius Paredes: não é isso?  
Victor Godinho de Lima: mas como é que você sabe que o sid é incompatível?  
Alexander Gonzalez: Beh, mando un esemplo do volta.  
Vinicius Paredes: Aqui,  
Alexander Gonzalez: Verb  
Vinicius Paredes: aqui, ó, aqui em cima, não é isso? É onde que é onde ele vem o parecer da IA mesmo.  
Victor Godinho de Lima: Não.  
Vinicius Paredes: E é só Exato.  
Victor Godinho de Lima: Aí a retornaria isso também.  
Alexander Gonzalez: aqui.  
Vinicius Paredes: Ele vai retornar as duas coisas.  
Victor Godinho de Lima: Ah,  
Vinicius Paredes: É isso que eu tô falando.  
Victor Godinho de Lima: ah,  
Willian Martinez: Sim, sim,  
Victor Godinho de Lima: tá bom.  
Willian Martinez: sim. É, achei que tava falando outro  
Vinicius Paredes: Não, não.  
Willian Martinez: também.  
Vinicius Paredes: Ele vai retornar as duas coisas.  
Victor Godinho de Lima: Sim,  
Vinicius Paredes: A gente tá discutindo.  
Victor Godinho de Lima: as duas.  
Vinicius Paredes: É só isso aqui, ó. Só o checklist aí.  
Victor Godinho de Lima: Aham.  
Vinicius Paredes: O, esse texto aqui,  
Victor Godinho de Lima: Aham.  
Vinicius Paredes: ó. Esse texto aqui é só esse texto aqui,  
Victor Godinho de Lima: Sim,  
   
 

### 00:39:00

   
Vinicius Paredes: entendeu?  
Victor Godinho de Lima: sim, sim.  
Vinicius Paredes: Esse esse status aqui é só o o iconezinho aqui,  
Victor Godinho de Lima: Aham. Sim. Não,  
Willian Martinez: Mas isso vai ser gerado pela EA  
Victor Godinho de Lima: eu eu eu fiz o comentário só.  
Vinicius Paredes: entendeu?  
Willian Martinez: 100%.  
Victor Godinho de Lima: Eu fiz o comentário só porque eu na hora que você saiu, eu comentei desse cara aí com o Alex, essa lista aí. Aí eu só conectei com ele que isso daí era sobre aquilo que a gente tava falando antes.  
Alexander Gonzalez: Sim.  
Vinicius Paredes: Boa.  
Alexander Gonzalez: O o olhe aí o que eu mandei no chat. Vini, por exemplo,  
Vinicius Paredes: M.  
Alexander Gonzalez: agora ele volta assim, entende? Ele validou esse procedimento, esse código voltar no autorquestra motivo glossa, procedimento, sabe? para procedimiento os  
Willian Martinez: É O texto seria esse carinha aí,  
Alexander Gonzalez: casos  
Willian Martinez: né? procedimento fora do r.  
Alexander Gonzalez: si alguma cosa assim penso vendo que além disso a gente precisaria dar uma mexida no texto e você quer que a gente também mande esse resuminho que está em verde lá em cima, que é como seria isso.  
Vinicius Paredes: É, eh,  
   
 

### 00:39:58

   
Willian Martinez: Угуm.  
Vinicius Paredes: precisa do resumo. É do resumo.  
Alexander Gonzalez: Ja.  
Vinicius Paredes: E o, os itens que tu, ó, cada item que tu mandou aqui, eh, que no caso é esse, esse agent análisis, né? Esse agent análisis, eh, tu teria que colocar eh, quais qual é o o ID dele, entendeu? Tipo, deixa eu ver um aqui, eh, do SID aí, ó. É SID confirmando o laudo, entendeu? Aí, ó, tá faltando e ausência do Sid. Isso aqui é a regra da Nesk, né?  
Willian Martinez: Isso é, isso é a tag de um do de um dos itens do checklist. É isso,  
Vinicius Paredes: Isso é a tag, por exemplo, do evento eh 40,  
Willian Martinez: tá?  
Vinicius Paredes: 30, 22 ali, entendeu?  
Willian Martinez: Ah, tá bom. Beleza? Então, o se a gente vai receber só a tag, de certa forma os textos vão estar do nosso lado.  
Vinicius Paredes: Então, aí era outra,  
Willian Martinez: É isso?  
Vinicius Paredes: isso aí foi outra pergunta que eu fiz. Será que é mais interessante ficar do nosso lado ou ou já retornar tudo junto lá da da de inteligência,  
   
 

### 00:41:30

   
Willian Martinez: Porque eu eu ia perguntar exatamente isso,  
Vinicius Paredes: entendeu?  
Willian Martinez: se o a as respostas de texto que a gente tem hoje, ela é gerada automaticamente ou a gente tem uma lista e a gente devolve, olha para essa lista e fala: "Aquele cara se encaixa ali e devolve  
Alexander Gonzalez: Porque estos textos,  
Willian Martinez: ele?  
Alexander Gonzalez: olha, por exemplo, esse caso que eu mandei idade fora da faixa permitida. Um texto genérico da regra, tá? Mas eh está mais padronizado para o o motivos  
Vinicius Paredes: Isso é um texto genérico. Pode,  
Alexander Gonzalez: glossas.  
Willian Martinez: Tá.  
Vinicius Paredes: cara, eu acho melhor deixar isso aqui engenharia, já que é um um texto genérico, mais de de checklist assim mesmo.  
Alexander Gonzalez: Então eu te passo assim como está e você transforma num texto mais  
Vinicius Paredes: E e o ID é, passa o ID, passa o ID que aí eles vão,  
Alexander Gonzalez: bonito.  
Vinicius Paredes: a gente vai fazer esse, esse no caso o o Natan vai fazer até sexta-feira, né, que ele falou esse essa lista de objetos aqui, contexto, status, severidade e tudo.  
Alexander Gonzalez: Bom, e mais uma dúvida aí,  
Willian Martinez: É,  
Vinicius Paredes: Beleza?  
Willian Martinez: eu posso  
Vinicius Paredes: Só vai ter que aí tu vai ter que pegar esse ID depois e e botar lá também no teu que aí tu vai ter que retornar  
   
 

### 00:42:34

   
Alexander Gonzalez: Vini?  
Victor Godinho de Lima: Eu  
Vinicius Paredes: o ID, né? Isso aqui, ó.  
Willian Martinez: Uhum.  
Vinicius Paredes: Tão vendo a tela aí,  
Willian Martinez: Ô Vini, será que eh deixa eu fazer uma provocação,  
Vinicius Paredes: né?  
Willian Martinez: será que não faz sentido estar em DS? Porque aí é um ponto só que a gente vai ter que alterar, porque se se acontecer qualquer alteração, a gente tem que alterar as tags que D vai mandar pra gente e os textos que a gente tem.  
Victor Godinho de Lima: também preferiria que estivesse em DS, senão vai ficar um altera lá, altera aqui, altera lá, altera aqui.  
Willian Martinez: Ah, pode estar descincado a eu tô falando isso porque eu já tive problema com isso,  
Victor Godinho de Lima: S.  
Willian Martinez: principalmente notificação. Aí, aí depende que o Alex o Alex pra  
Alexander Gonzalez: Não, acho que podia ficar, tá? O que a gente quer definir bem qual é o o formato,  
Willian Martinez: gente.  
Vinicius Paredes: Bom, então,  
Alexander Gonzalez: porque no final das contas a gente que vai validar regra, sabe? Então assim como o o que eu mandei,  
Willian Martinez: Uhum. É,  
Alexander Gonzalez: a gente precisa definir bem.  
Willian Martinez: o que vai mudar é quem vai fazer o map disso,  
   
 

### 00:43:19

   
Vinicius Paredes: He.  
Willian Martinez: né? O que vai mudar é quem vai fazer o  
Alexander Gonzalez: Exato. O que a gente precisa é definir isso, como a gente faz esse esse mapeamento do do textinho.  
Willian Martinez: map.  
Alexander Gonzalez: Eu acho que eu podia fazer, mas o que eu preciso é esse esse mapeamento de como a gente  
Vinicius Paredes: Beleza. O contrato a gente vai esperar isso aqui agora.  
Willian Martinez: Fechou.  
Vinicius Paredes: Agora é contigo.  
Alexander Gonzalez: bom. OK.  
Vinicius Paredes: Aí eu vou até tirar essa essa essa dúvida aqui, ó, de quem ficaria o a responsabilidade.  
Alexander Gonzalez: Tá, coloca que fica com a gente.  
Vinicius Paredes: Eh, boa. Tá gravado aqui,  
Alexander Gonzalez: Não,  
Vinicius Paredes: tá?  
Alexander Gonzalez: tá bom. Preciso quem vai definir a verdade pelo menos a verdade é o Natal.  
Vinicius Paredes: Eh,  
Alexander Gonzalez: Isso vai de  
Vinicius Paredes: é, ele vai ele vai definir os valores, só vai utilizar esse esse esse catálogo  
Alexander Gonzalez: valores. Mais uma dúvida Vini é no outro que você mandou tem um textinho lá em cima que é como um resumo  
Vinicius Paredes: dele  
Willian Martinez: Угу.  
Alexander Gonzalez: daí é no no quando você vai lá no no visual.  
Vinicius Paredes: aqui.  
Alexander Gonzalez: Esse texto também a ideia é que se um  
   
 

### 00:44:38

   
Victor Godinho de Lima: A ideia é que seja um texto que vocês vão mandar.  
Vinicius Paredes: Eh,  
Alexander Gonzalez: não, mas é que tô pensando que um texto assim longo,  
Vinicius Paredes: eh.  
Alexander Gonzalez: não sei se dá a daí precisaria do Davi do ou do Nathan para pra gente fazer um padrão, sabe, de de texto aí de resumo.  
Vinicius Paredes: Cara, eu acho que isso aqui é um é um um sumarizer de de todas as os apontamentos que ele fez ali, não é? Não é um resumo de tudo que ele achou ali de eventos.  
Alexander Gonzalez: Mas é que aí tá super Mas imagina que leva rodar 20 a gente fica  
Victor Godinho de Lima: É,  
Alexander Gonzalez: K.  
Victor Godinho de Lima: eu eu eu eu eu entendi qual que é seu ponto e e se eu fosse de DS, essa parte é a parte que eu teria mais dúvidas, porque você pega uma solicitação, você roda, crente falou, tem 30 agentes que vai rodar. Cada agente, não necessariamente faz só um IF de validação. Eh, o quanto, então imagina que no final das contas você pode ter passado ali por, sei lá, três condições de cada gente que foi checada. Então você tem aí 90 itens. Quantos desses são importantes o bastante para aparecer ali como o chequezinho verde lá embaixo ou quais que foram sucesso, mas não vale essa menção horrosa?  
   
 

### 00:46:07

   
Victor Godinho de Lima: E como que você faz um resumo de, sei lá, 20 palavras? O que que você engloba nesse resumo? Eh, quais que você coloca dentro ou não?  
Alexander Gonzalez: essa  
Victor Godinho de Lima: Eh, eu eu também não sei. tem que analisar aí uma uma ideia, mas eh eu também não sei.  
Vinicius Paredes: Fala aí, Davi.  
Alexander Gonzalez: Ah, o David já definiu como a ideia  
Davi Rojtenberg: É assim, o o que como eu vejo, né, a ideia é uma é um agente que vai mastigar isso tudo. Ele vai seguir uma uma série de de regras determinadas por hierarquia e vai cuspir ali um parágrafo dizendo: "Ó, na na minha visão aqui de tudo que foi avaliado, tem mais positivos do que negativos, então aprova." O tanto que ele ele não coloca lá a decisão como a prova. Ele fala: "Tem a tendência é aprovar ou a tendência é negar". Eu vi muita coisa no meu checklist tem coisa negativa, então a minha recomendação é é negar. Eu acho que é é muito mais por um modelo estatístico do que um modelo eh sólido e  
Alexander Gonzalez: É que a gente pode fazer o modelo.  
Vinicius Paredes: Determiní.  
Alexander Gonzalez: O problema para mim é o texto,  
   
 

### 00:47:15

   
Davi Rojtenberg: exatamente  
Alexander Gonzalez: porque se você me fala, não fale um score que tão bom ou ruim, é fácil, mas falar o texto, sabe?  
Davi Rojtenberg: é porque na verdade assim ele pega no checklist ali os cinco principais assim que são que são geralmente o que determinam a a o que levam é a concluir se é prova ou não aprova.  
Alexander Gonzalez: Yeah.  
Davi Rojtenberg: Então ele baseado naquilo, ele vai dizer: "Ó, de tudo que eu vi aqui, isso aqui é complicado, entendeu? Ele vai definir ali o que que para ele é o ponto mais complicado. Você fala, monta ali um texto ali, um parágrafo de coloca um limitador de caracter e os modelos geradores de texto são ótimos em fazer blá blá e vai ser um blá blá mesmo. A ideia, na verdade, é a cor, é assim, aprova, não aprova, porque no fim das contas, vou te falar, para autorizador, isso não vai importar muito não, porque ele pode ir lá e até reescrever isso aí depois quando ele for colocar na aprovar, ele tem lá justificativa, ela já vem, vamos dizer assim, copiando esse texto, mas ele pode ir lá e editar isso aí se ele quiser mudar alguma coisa, simplesmente manda para pra frente. Dificilmente alguém vai voltar lá no histórico para dar uma lida no texto que a Iá disse, entendeu?  
   
 

### 00:48:22

   
Davi Rojtenberg: Isso é o de menos.  
Vinicius Paredes: O que eu o que eu acho aqui, ô ô, Alex, eh a tu tu gerou esse esse esse responso final aí, né, que tem os event que tu achou, certo? Eh,  
Alexander Gonzalez: Sì.  
Vinicius Paredes: tu vai pegar todos esses motivos aí e mandar uma IA fazer um um resumo, entendeu, desses motivos aí que aí é o que Davi falou, coloca um um limite de palavras, limite de caracteres, enfim, entendeu?  
Alexander Gonzalez: É que eu acho mandaria fazer esse resumo. Não sei se eu vou de mas vou pensar, tá? Porque se fosse uma frase, um status que a gente definir tudo bem. Ah, passou toda a inteligência quando é bom. Reprovou tales, sabe? é diferente, mas tem cinco opções e você manda  
Vinicius Paredes: O problema é que tu dificilmente vai ter O problema é que dificilmente tu vai ter solicitações com os mesmos checklists aqui, entendeu? Com o mesmo checklist.  
Davi Rojtenberg: Sim,  
Vinicius Paredes: Então tu montar uma frase pronta,  
Davi Rojtenberg: são são de é dá uma olhada,  
Vinicius Paredes: cara, vai ter quantas frases? Entendeu?  
Davi Rojtenberg: ó, dá uma olhada no exemplo.  
Vinicius Paredes: levando uma combinação.  
   
 

### 00:49:35

   
Vinicius Paredes: No.  
Davi Rojtenberg: Dá uma olhada no exempl que eu coloquei aí no chat. Você vai ver que assim,  
Willian Martinez: M.  
Davi Rojtenberg: ele pega os pontos característicos, assim, aqueles que são mais importantes dentro de toda a avaliação que ele fez, as coisas óbvias, ele tá ignorando, mas tem um detalhe ali que a esse aqui realmente é a prova, esse aqui não, esse aqui nega, n você vê que ele pega o detalhe, ele não ele não pega tudo, ele não faz um review geral e te dá um texto do resumo geral, ele pega o que é mais importante pra decisão da IA. É, é isso, pelo menos o que tá sendo sugerido em layout. Eu não sei se isso é possível na prática, mas é a a minha ideia é isso.  
Alexander Gonzalez: Eu vou vou pensar, tá? Como fazer isso, mas eu não sei se testou ver quantos caracteres podia ter o testo.  
Victor Godinho de Lima: Estás muteado.  
Alexander Gonzalez: Oi, olá,  
Vinicius Paredes: Tá mudo. Davi,  
Alexander Gonzalez: olá.  
Vinicius Paredes: Davi.  
Alexander Gonzalez: Nada.  
Davi Rojtenberg: Então, a ideia, a ideia seria assim, eh, definir a regra,  
Vinicius Paredes: Mudo.  
Davi Rojtenberg: ó, pro modelo um parágrafo vai até 250 caracteres no máximo, entendeu?  
   
 

### 00:50:40

   
Davi Rojtenberg: não passa disso. E assim, os modelos de texto são ótimos nesse sentido. Ele vai conseguir pegar ali, montar alguma coisa que vai dar algum tipo de embasamento pro pro usuário. E como eu disse assim, isso tem uma tem uma certa importância, mas não é não é mandatório. Mandatório é a checklist. A checklist é onde o o onde o bicho pega.  
Alexander Gonzalez: บ  
Vinicius Paredes: Boa. Aí tem aqui o módulo de interface, tem aqui uns big numbers eh com com as devolutivas, né? Aí, ô, ô Davi, essa essa parte de evolutivas aí, eh, tu tem o M1 em algum e algum vel da vida aí?  
Victor Godinho de Lima: O verso da M1.  
Vinicius Paredes: É.  
Victor Godinho de Lima: Opa, tô mandando aqui  
Vinicius Paredes: Tá, tá arrumando já.  
Victor Godinho de Lima: aqui, ó.  
Vinicius Paredes: Eu tava  
Victor Godinho de Lima: Ah, opa,  
Vinicius Paredes: tod  
Victor Godinho de Lima: já esse que o David deixou no hot key do do F1 2 3  
Vinicius Paredes: boa devolutivas aqui. Eh, e isso aqui é é é basicamente um atalho, não é isso?  
   
 

### 00:52:17

   
Davi Rojtenberg: Угуm.  
Vinicius Paredes: pro pro pra fila operacional com filtro,  
Davi Rojtenberg: Угу.  
Vinicius Paredes: não é isso? Tá ver outro ponto ali.  
Davi Rojtenberg: Yes.  
Vinicius Paredes: Hum. Tá histórico.  
Davi Rojtenberg: Eu não sei se M1 tem, mas eu acho que tem. Eh, ele tem uma simulação de retorno,  
Vinicius Paredes: Simulação de  
Davi Rojtenberg: tem simulação de retorno. Se você clicar num num pedido de evolutiva, ele mostra como é que tá atuando.  
Vinicius Paredes: retorno.  
Davi Rojtenberg: Aí, clica num primeirão aí, ó. Tá vendo? Tá falando assim, ó. Tá em pendência. Aí tem ali, ó, processar retorno do prestador. Isso aí é como seria a resposta quando a gente recebe uma simulação mesmo. Pode clicar nele. Ó lá, ele recebeu. Aí ele já aí a reprocessou e ela tá agora reprocessando. O a decisão dela, viu que ela mudou o ponto de vista e mudou o checklist? Se você quiser rever, vai em usuário ali no menu usuário.  
   
 

### 00:53:29

   
Davi Rojtenberg: Clica ali no menu usuário e bota assim, ó. Reetar processo. Ah, que máximo é mágico. Gostou do gostou  
Vinicius Paredes: Que f***, velho. Tá f*** isso aqui,  
Davi Rojtenberg: da É um  
Vinicius Paredes: ó. Ele fez até um um um como é o nome daquele daquele o o stereg aqui de  
Davi Rojtenberg: reset?  
Vinicius Paredes: reprocessar, saco. Botou escondidinho aqui no menu do usuário, cara.  
Davi Rojtenberg: Não, mas é p Mas é para você. É porque a brincadeira só nossa, né? A brincadeira não é pros outros.  
Victor Godinho de Lima: Cara, você sabe que eu trabalhei numa empresa que tinha um vendia sistema de Omniteni e tinha uma graça e tinha até uma graça com os clientes eh easterg. Então, tipo, tinha uma tela lá que você apertava ES três vezes, o logo da empresa fazer um negócio e voltava, tipo uns negocinos meio bobo assim,  
Vinicius Paredes: Não dá,  
Victor Godinho de Lima: mas os clientes,  
Vinicius Paredes: velho.  
Victor Godinho de Lima: os clientes pirava em querer descobrir os stereg,  
Vinicius Paredes: Não dá ideia pro Davi não,  
   
 

### 00:54:23

   
Victor Godinho de Lima: o caramba.  
Vinicius Paredes: Gotinho. p***  
Davi Rojtenberg: Não, não,  
Vinicius Paredes: m****.  
Davi Rojtenberg: mas saí aí. Isso aí foi, na verdade, porque eu imagino que vocês vão querer, vão em algum momento vão perguntar assim: "Tá bom Davi, mas beleza, tá? Pedi até impendência, mas o que que acontece depois que recebe?" Tá aí, tá respondido. Você vê que ele muda o checklist,  
Vinicius Paredes: Boa.  
Davi Rojtenberg: o Jacklist tava vermelhinho, aí ele passa a ficar todo verdinho do tipo. Beleza, agora vai.  
Vinicius Paredes: Ó, tá aqui, ó. O sistema de chip é recebido com devolutivo no documento retornado pelo prestador.  
Davi Rojtenberg: Pô, a experiência tá boa, velho. Não tô  
Vinicius Paredes: Boa. Eh,  
Davi Rojtenberg: buscando  
Vinicius Paredes: aí isso aqui é mais pra gente backend, tá? Eh, depois o acho que eu eu e o eu e Godin vai melhorar isso aqui, discutir melhor isso aqui. Eh, requisitos funcionais, eu acho que também não precisa entrar em detalhes.  
   
 

### 00:55:26

   
Vinicius Paredes: Eh, aí tem alguns pontos aqui que eu coloquei como lacunas e riscos, tá? aqui. Ô, ô, ô Davi, eh, eu queria que tu desse uma olhada também e tentasse eh responder o que tu acha que tu consegue. Isso aqui foram foram pontos que a gente identificou de de atenção. Por exemplo, tem tem um um documento lá da NS, cadê? achar qual é o o que ele achou com SLA em tempos diferentes.  
Victor Godinho de Lima: É um que tá com vermelho aí. G18.  
Vinicius Paredes: Ei, ó, SLA tem uma resolução que tá com 5 dias para TA e tem outra que tá com 10 dias, tá? Eh, aí isso aqui eu coloquei, a gente colocou como ponto de de de dúvida porque a gente não sabe qual que vale, entendeu? Ele regulatório suspende. Esse aqui foi respondido já, né? Tá. Conta médica, suspeção de três dias também já foi respondido. Eu vou processar depois e atualizar tudo isso aqui, tá?  
Davi Rojtenberg: Beleza.  
Vinicius Paredes: Aí o checklist, o item do do checklist lá que a gente discutiu.  
Davi Rojtenberg: Я  
Vinicius Paredes: Aí aqui é de de engenharia.  
   
 

### 00:57:07

   
Vinicius Paredes: Boa. Eh, cara, é isso. algum algum ponto, algum alguma coisa queira colocar aqui como  
Victor Godinho de Lima: Não,  
Vinicius Paredes: dúvida?  
Willian Martinez: Vai surgir.  
Victor Godinho de Lima: passamos por vários itens aí.  
Willian Martinez: Что?  
Victor Godinho de Lima: Eh, meus úos pontos só são aqueles ali pra gente fechar o contrato e aí, Alex, eh, das nossas integrações. Eu acho que eh me preocupa mais esses pontos de amarrações aí depois de a gente pegar mensagem de fila e caramba, você precisava do número da carteirinha, sabe? Eu acho que isso aí me preocupa mais do que até o nosso alinhamento aqui com com Davi. Acho que esse tá tá mais fácil e é mais palpável,  
Alexander Gonzalez: Tá  
Victor Godinho de Lima: né, ali na tela e tal.  
Alexander Gonzalez: bom.  
Victor Godinho de Lima: Inclusive a gente vai ter algumas mudanças ali, né? O o end point ali do da análise do OCR ali, ele não tá retornando todos os campos que a gente precisa, né?  
Alexander Gonzalez: Não, agora  
Willian Martinez: O a agora tá agora tá devolvendo boa parte dele.  
Victor Godinho de Lima: Tá. Boa parte. Falta  
Willian Martinez: Acho que o pelo que eu entendi,  
   
 

### 00:58:26

   
Victor Godinho de Lima: alguns.  
Willian Martinez: que foi o que eu conversei com o com o Luig, depende do tipo de arquivo. Tem arquivo que retorna um tipo de coisa, retorna uma quantidade de coisa, tem arquivo que retorna outra quantidade de coisa. depende do que tá no arquivo,  
Victor Godinho de Lima: Tá.  
Willian Martinez: sabe?  
Victor Godinho de Lima: Acho que data de nascimento tá  
Willian Martinez: Então o acho que a data depois se não me engano,  
Victor Godinho de Lima: retornando.  
Willian Martinez: não tem no arquivo.  
Victor Godinho de Lima: Ah, não tem.  
Willian Martinez: É, entendeu? Tem umas coisas que não tem no arquivo e aí não não vem. Se tiver, pelo que eu entendi, se tiver, vem. Então tem alguns arquivos que eu queria testar.  
Alexander Gonzalez: Todo que ele encontra volta ou ou melhor tudo que ele identifica,  
Willian Martinez: É exato.  
Alexander Gonzalez: pod que tenha e ele não identifica, ele erra,  
Willian Martinez: É,  
Alexander Gonzalez: mas se ele identifica, ele  
Willian Martinez: inclusive um dos que um dos que você mandou,  
Alexander Gonzalez: manda.  
Willian Martinez: Godinho, ontem parece que ele foi mexido com o chat PT, até tem umas umas letras meio esquisitas assim,  
Vinicius Paredes: O  
Willian Martinez: sabe? Mas ele, boa parte dele ele identifica. Só que eu eu queria que a gente tivesse a gente tivesse alguns arquivos com CPF, com carteirinha, pra gente conseguir validar essa extração  
Victor Godinho de Lima: Ô, ô, Alex, você tem uns umas guias legais  
Willian Martinez: real.  
Victor Godinho de Lima: aí?  
Alexander Gonzalez: com CPF acho que não, mas com cartelinha tem. O que eu mandei não tinha cartelinha e tem matrícula.  
Victor Godinho de Lima: Eu acho que um daqueles lá,  
Alexander Gonzalez: A matrícula da carteirinha.  
Victor Godinho de Lima: um dos daqueles três lá tem,  
Alexander Gonzalez: Olha o  
Victor Godinho de Lima: acho que  
Vinicius Paredes: É que o dona dono banana não conseguia fazer o não.  
Alexander Gonzalez: o ID matric tem um campo na esquerda acima que aí tem o o a matrícula perto do nome ver. Ah, manda parabolinha.  
Willian Martinez: O que eu falei que parece que foi mexido é esse Mariana Melo. Tem tem umas letras que não dá para identificar mesmo, não.  
Alexander Gonzalez: Ah,  
Victor Godinho de Lima: Ó,  
Alexander Gonzalez: mas é porque ele assim  
Victor Godinho de Lima: o primeiro No.**