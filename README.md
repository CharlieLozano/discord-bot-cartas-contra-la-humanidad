# Cartas contra la humanidad / Discord Bot
###### Cards against Humanity / Discord Bot
Este bot cuenta con una recreación del juego de mesa de Cartas contra la Humanidad (CaH: Cards Against Humanity).

## Premisa
Construye las frases más inapropiadas con tus amigos y descubre quien es el más descarado.

## ¿Cómo iniciar un juego?
1. `.m cah crear` para crear una partida.
2. Para invitar a los jugadores existen dos comandos:
    - `.m cah invitaciones abiertas` creara un mensaje público donde las demás personas podrán unirse.  Si se quiere cerrar las invitaciones existe el comando `.m cah invitaciones cerradas`
    - `.m cah invitar [@usuario]` le enviará una invitación a dicho usuario. Esto funciona incluso cuando las invitaciones están cerradas.
3. Una vez que todos los jugadores estén dentro, usa el comando de `.m cah iniciar` Y el juego se hará cargo del resto. 

## ¿Cómo se juega? 
*Se interactúa con el juego usando las reacciones de discord.*

### Objetivo
Gana la persona que haya acumulado más puntos por votaciones del Juez. Y la dinámica consiste en completar o responder frases y preguntas usando cartas que serán repartidas a lo largo del juego.

### Etapa para Revelar
Al inicio de cada turno se asignará a un juez en donde tendrán que reaccionar a un mensaje con la palomita para revelar una pregunta o frase.

### Etapa de Selección
Se les repartirá por privado cartas a los demás jugadores y tendrán que escoger la carta o cartas que mejor completen o respondan a la carta que se reveló.

### Etapa de Votos
Una vez que todos los jugadores hayan seleccionado sus cartas, habrá una votación popular y una votación para el juez donde se mostrarán todas las opciones elegidas.

- **Votacion del Juez:** Esta será enviada al juez por privado y únicamente se podrá podrá escoger una opción. Este voto es el que más peso tiene ya que el jugador con más votos por parte de los jueces será el ganador.
- **Votación Popular:** Está es una votación en la cual todos pueden votar, incluyendo el mismo juez y espectadores. También se puede votar por múltiples opciones. Al final del juego los jugadores que más votos populares tengan tendrán el premio de los jugadores más populares.

*Los votos por uno mismo en la votación popular no serán contados.*

### ¿Que sucede en caso de empate?
Al final del juego, en caso de empate por votos del juez, se usará el voto popular para determinar el desempate. Si vuelve a haber un empate, las personas involucradas serán consideradas las ganadoras.

### Termino de turno e inicio del siguiente
Cuando el juez haya votado se anunciará al ganador y nuevamente iniciará el turno y se le asignará el rol de juez al siguiente jugador y este procedimiento se repetirá hasta que termine el juego.

### Rondas y Fin del juego
El juego se termina cuando se hayan terminado de jugar las rondas restablecidas. Una ronda es el conjunto de turnos donde todos ya participaron como jueces. Dos rondas se significa que todos los jugadores serán jueces dos veces.

Por defecto el juego ya tiene un número determinado de rondas dependiendo el número de jugadores. Si son muchos será solo una ronda, o más rondas si son menos jugadores.

Para determinar el número de rondas, antes de que se inicie el juego, se puede usar el comando de `.m cah rondas [número de rondas]`.

### Ganadores
 Una vez que hayan terminado las rondas el juego dará los honores y anunciará al ganador del juego y al ganador del voto popular.
 
## Decks
Existe un deck de cartas adicional creado para la comunidad bonóbica. Para seleccionar el deck se pueden usar los siguientes comandos:

`.m cah deck default` *El original*
`.m cah deck bonobo` *El deck de los bonobos*
`.m cah deck full-bonobo` *El deck original combinado con el de los bonobos*
 
## Preguntas Frecuentes
- Me salen las mismas cartas!
El bot recrea la dinámica del juego de mesa, en donde la carta que juegas será descartada y tomas una nueva carta para volver al número inicial de cartas. Las demás cartas permanecerán.

- Ya seleccioné una carta pero no pasa nada
Verifica cuantas cartas pide el juego. Hay cartas que tendrán que ser respondidas con más de una carta.

- ¿Qué es un Haiku?
Es un estilo de poesía japonés que consta de tres versos, está carta tendrá que ser respondida por otras 3 cartas.
 
## Comandos
 `.m cah crear` *Crea una partida*
`.m cah iniciar` *Inicia el juego*
`.m cah invitar [usuarios]` *Invita a personas en específico*
`.m cah invitaciones [abiertas/cerradas]` *Abre o cierra las invitaciones públicas*
`.m cah admin [vacio(para información) / usuarios]` *Da permisos a otra persona para que tenga acceso a todos los comandos durante una partida*
`.m cah unadmin [usuarios]` *Retira los permisos de administrador a otra persona*
`.m cah rondas [número de rondas]`*Asigna el número de rondas a jugar*
`.m cah expulsar [usuarios]` *Expulsa a un jugador*
`.m cah salir` *Sal de la partida*
`.m cah deck [vacio(para información) /nombre del deck]` *Escoge un deck*
`.m cah saltar` *Salta el turno*
`.m cah destrabar` *En caso de que el juego se haya trabado se puede usar este comando para saltar al siguiente turno o etapa*
`.m cah terminar` *Terminar el juego*