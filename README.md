# Cartas contra la humanidad / Discord Bot
###### Cards against Humanity / Discord Bot
Este bot cuenta con una recreación del juego de mesa de Cartas contra la Humanidad (CaH: Cards Against Humanity).

## Premisa
Construye las frases más inapropiadas con tus amigos y descubre quien es el más descarado.

## ¿Cómo iniciar un juego?
En el canal donde desees jugar utiliza los siguientes comandos:

1. `.cch crear` para crear una partida.
2. Para invitar a los jugadores existen dos comandos:
    - `.cch invitaciones abiertas` creara un mensaje público donde las demás personas podrán unirse.  Si se quiere cerrar las invitaciones existe el comando `.cch invitaciones cerradas`
    - `.cch invitar [@usuario]` le enviará una invitación a dicho usuario. Esto funciona incluso cuando las invitaciones están cerradas.

    :eye: Los jugadores podrán ser invitados incluso ya una vez que comenzó el juego.
3. Una vez que todos los jugadores estén dentro, usa el comando de `.cch iniciar` Y el juego se hará cargo del resto. 

## ¿Cómo se juega?
*Se interactúa con el juego usando las reacciones de discord que aparecerán en los mensajes.*

- **Revela:** Al inicio de cada turno se asigna a un juez que revelará una pregunta o una frase incompleta.
- **Elige:** Los demás jugadores tendrán que contestar o completar la frase que se reveló usando las cartas que se les estarán repartiendo
- **Votación**: Después de que todos hayan jugado, el juez escogerá la opción que más le haya gustado; ya sea la más descarada, o la que más le haya causado gracia, etc. :warning: *La votación del Juez será enviada por mensaje privado!*
- **Puntos**: La persona elegida por el juez gana un punto y comienza el siguiente turno.
- **Final**: Cuando termina el juego gana la persona que más puntos haya obtenido.

## Más información sobre cada parte.

### :mag_right: Etapa para Revelar
El juez tendrá que ser la persona que reaccione con la palomita verde para que revele la pregunta.

### :thinking: Etapa de Selección
Hay frases que requieren más de una carta, en este caso los jugadores tendrán que escoger las cartas en el orden que deseen que aparezcan.

### :scroll: Etapa de Votos
Una vez que todos los jugadores hayan seleccionado sus cartas, habrá una votación popular y una votación para el juez donde se mostrarán todas las opciones elegidas.

- :man_judge: **Votacion del Juez:** Esta será enviada al juez por privado y únicamente se podrá podrá escoger una opción. Este voto es el que más peso tiene ya que el jugador con más votos por parte de los jueces será el ganador.
- :people_holding_hands: **Votación Popular:** Está es una votación en la cual todos pueden votar, incluyendo el mismo juez y espectadores que no se encuentrne jugando. También se puede votar por múltiples opciones. Al final del juego los jugadores que más votos populares tengan tendrán el premio de los jugadores más populares.

:warning: *Los votos por uno mismo en la votación popular no serán contados.*

### :balance_scale: ¿Que sucede en caso de empate?
Al final del juego, en caso de empate por votos del juez, se usará el voto popular para determinar el desempate. Si vuelve a haber un empate, habrá más de un ganador.

### :alarm_clock: Término de turno e inicio del siguiente
Cuando el juez haya votado se anunciará al ganador y nuevamente iniciará el turno y se le asignará el rol de juez al siguiente jugador y este procedimiento se repetirá hasta que termine el juego.

### :revolving_hearts: Rondas y Fin del juego
El juego se termina cuando se hayan terminado las rondas establecidas. 

Una ronda es el conjunto de turnos donde todos ya participaron como jueces. Dos rondas se significa que todos los jugadores serán jueces dos veces.

Por defecto el juego ya tiene un número determinado de rondas dependiendo el número de jugadores. Si son muchos será solo una ronda; Si son menos serán más rondas.

Para determinar el número de rondas, antes de que se inicie el juego, se puede usar el comando de `.cch rondas [número de rondas]`.

### :confetti_ball: Ganadores
 Una vez que hayan terminado las rondas el juego dará los honores y anunciará al ganador del juego y al ganador del voto popular.
 
## Decks
Existe un deck de cartas adicional creado para la comunidad bonóbica. Para seleccionar el deck se pueden usar los siguientes comandos:

`.cch deck default` *El original*  
`.cch deck bonobo` *El deck de los bonobos*  
`.cch deck full-bonobo` *El deck original combinado con el de los bonobos*
 
## Preguntas Frecuentes
- **Me salen las mismas cartas!**  
El bot recrea la dinámica del juego de mesa, en donde la carta que juegas será descartada y tomas una nueva carta para volver al número inicial de cartas. Las demás cartas permanecerán.

- **Ya seleccioné una carta pero no pasa nada**  
Verifica cuantas cartas pide el juego. Hay cartas que tendrán que ser respondidas con más de una carta.

- **¿Qué es un Haiku?**  
Es un estilo de poesía japonés que consta de tres versos, está carta tendrá que ser respondida por otras 3 cartas.
 
## Comandos
`.cch crear` *Crea una partida*  
`.cch iniciar` *Inicia el juego*  
`.cch invitar [usuarios]` *Invita a personas en específico*  
`.cch invitaciones [abiertas/cerradas]` *Abre o cierra las invitaciones públicas*  
`.cch admin [vacio(para información) / usuarios]` *Da permisos a otra persona para que tenga acceso a todos los comandos durante una partida*  
`.cch unadmin [usuarios]` *Retira los permisos de administrador a otra persona*  
`.cch rondas [número de rondas]` *Asigna el número de rondas a jugar*  
`.cch expulsar [usuarios]` *Expulsa a un jugador*  
`.cch salir` *Sal de la partida*  
`.cch deck [vacio(para información) /nombre del deck]` *Escoge un deck*  
`.cch saltar` *Salta el turno*  
`.cch destrabar` *En caso de que el juego se haya trabado se puede usar este comando para saltar al siguiente turno o etapa*  
`.cch terminar` *Terminar el juego*
 `.cch crear` *Crea una partida*  
`.cch iniciar` *Inicia el juego*  
`.cch invitar [usuarios]` *Invita a personas en específico*  
`.cch invitaciones [abiertas/cerradas]` *Abre o cierra las invitaciones públicas*  
`.cch admin [vacio(para información) / usuarios]` *Da permisos a otra persona para que tenga acceso a todos los comandos durante una partida*  
`.cch unadmin [usuarios]` *Retira los permisos de administrador a otra persona*  
`.cch rondas [número de rondas]` *Asigna el número de rondas a jugar*  
`.cch expulsar [usuarios]` *Expulsa a un jugador*  
`.cch salir` *Sal de la partida*  
`.cch deck [vacio(para información) /nombre del deck]` *Escoge un deck*  
`.cch saltar` *Salta el turno*  
`.cch destrabar` *En caso de que el juego se haya trabado se puede usar este comando para saltar al siguiente turno o etapa*  
`.cch terminar` *Terminar el juego*