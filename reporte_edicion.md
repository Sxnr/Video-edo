# Reporte de edición — Video del póster "Enfriamiento de la leche (Ley de Newton)"

> Punto de control antes del render. Generado por `scripts/report.py`.

## Estado

- Descargados y verificados con `ffprobe` los 6 videos y `procedimiento_edo.png` (ninguno era página de permiso).
- **No hay póster** (ni PDF ni imagen) en la carpeta de Drive ni en el chat → **falta `input/poster.png` o `poster.pdf` para renderizar.**
- **No hay `input/music.mp3`** → por ahora el video va sin música.
- Videos normalizados a 1920×1080, 30 fps CFR, H.264 + AAC 48 kHz mono, −16 LUFS (`loudnorm`), `highpass=80` + `afftdn` suave.
- Transcripción: whisper.cpp `large-v3-turbo` en español. Como sus marcas por palabra venían corridas hasta ~1,5 s, se re-alinearon con alineación forzada (torchaudio MMS_FA, ~20 ms de precisión) para que subtítulos y énfasis calcen ±100 ms.

### Videos de Adonis

- `video_20261110_102620.mp4` (10:26) → **Sección 1** (0:00–0:38: presentación, motivación, pregunta). Su segunda mitad (0:39–1:05) es una primera toma de la metodología.
- `video_20261110_110535.mp4` (11:05) → **Sección 3** (toma repetida y más completa de la metodología: agrega duración, registros cada 2 min, Alexa y 16 registros). Se descarta el tramo duplicado del primer video.

### Clasificación de cada grabación

| Hablante | Archivo | Formato original | Tipo | En el video |
|---|---|---|---|---|
| Adonis | ambos `video_20261110_*.mp4` | 4K vertical (rotado 90°), 29,97 fps | Persona en cámara | PiP vertical |
| Vicente | `VicenteVideoPoster_P.mkv` | 1080p 60 fps, 8:26 | 0:00–2:20 cámara web; 2:20–8:26 **pantalla** (pizarra digital + webcam chica) | Secc. 2 y 4: PiP; secc. 5: solo voz + `procedimiento_edo.png` en 3D |
| Martina | `2026-11-09-125944640.mp4` | 1080×1920 HEVC vertical | Persona en cámara | PiP vertical |
| Francisco | `20261110_113712.mp4` | 1080p horizontal | Persona en cámara | PiP horizontal |
| Yeny | `conclusion_poster.mp4` | 480×854 vertical (baja resolución) | Persona en cámara | PiP vertical pequeño (para que no se note la resolución) |

## Duración

| # | Sección | Hablante | Fuente | Habla tras cortes |
|---|---|---|---|---|
| 0 | Intro (título, integrantes, profesores) | — | generada, sobre el saludo de Adonis | +1.5 s |
| 1 | Introducción y objetivo | Adonis Hernández | `video_20261110_102620.mp4` | 34.0 s |
| 2 | Marco teórico | Vicente Acevedo | `VicenteVideoPoster_P.mkv` | 26.1 s |
| 3 | Metodología | Adonis Hernández | `video_20261110_110535.mp4` | 39.2 s |
| 4 | Datos y análisis exploratorio | Vicente Acevedo | `VicenteVideoPoster_P.mkv` | 17.0 s |
| 5 | Formulación y resolución | Vicente Acevedo | `VicenteVideoPoster_P.mkv` | 50.0 s |
| 6 | Estimación de k y validación | Martina Cares | `2026-11-09-125944640.mp4` | 27.5 s |
| 7 | Propuesta de mejora | Martina Cares | `2026-11-09-125944640.mp4` | 26.2 s |
| 8 | Interpretación | Francisco Carrera | `20261110_113712.mp4` | 43.1 s |
| 9 | Conclusión | Yeny Zapata | `conclusion_poster.mp4` | 20.7 s |
| 10 | Anexo: uso de IA + fade a negro | — | generada | 8.0 s |

- Habla total: **283.8 s**; pausas de transición entre secciones: 8 × 0.4 s.
- **Duración total estimada: 4:56.5** (límite 5:00). Velocidad de voz: 1,00× (sin acelerar).

## Transcripción limpia por sección

_Texto tal como queda en el video (Whisper large-v3-turbo + alineación forzada + glosario). `/` = corte de pausa._

### 1. Introducción y objetivo — Adonis Hernández (0:00.0–0:34.0 del tramo de voz)

Hola, somos Adonis, Yeny, Vicente, Francisco y Martina. Estudiamos cómo se enfría la leche recién hervida. / Elegimos este fenómeno porque se puede medir con instrumentos simples / y porque la leche no se enfría a una velocidad constante, sino que pierde calor más rápido cuando está más caliente. / Nuestra pregunta fue cómo evoluciona la temperatura de la leche durante los primeros 30 minutos desde su punto máximo de calor / y qué tan bien la describe una ecuación diferencial de primer orden.

### 2. Marco teórico — Vicente Acevedo (0:34.0–1:00.1 del tramo de voz)

como marco teórico, / la ley de Newton, en donde aquí se evalúa en con qué rapidez un / cuerpo pierde calor, / tanto entre su temperatura del líquido y la temperatura ambiente. / la constante tiene un signo negativo, / que indica que la temperatura está bajando. / La T mayúscula es la temperatura del líquido, / y menos el T sub E, es la temperatura ambiente.

### 3. Metodología — Adonis Hernández (1:00.1–1:39.4 del tramo de voz)

Esta experiencia se realizó el 19 de octubre, tipo a las 3 de la tarde, / en una habitación cerrada, sin corrientes de aire, / para que el ambiente afecte lo menos posible en la experiencia. / Hervimos 250 ml de leche entera y la vertimos en una taza, obteniendo así nuestro tiempo cero en la experiencia. La experiencia en sí duró 30 minutos, cada 2 minutos se tomaban registros / de la temperatura de la leche, con ayuda de un termómetro, / y en la temperatura del ambiente nos apoyamos con Alexa, / y así obtuvimos un total de 16 registros.

### 4. Datos y análisis exploratorio — Vicente Acevedo (1:39.4–1:56.4 del tramo de voz)

en datos y análisis exploratorio, lo que se ve aquí, en este gráfico, es cómo decrece de manera constante casi, / durante los 30 minutos, de estar en 78,1 a llegar a los 51,4, / en el término de este experimento.

### 5. Formulación y resolución — Vicente Acevedo (1:56.4–2:46.3 del tramo de voz)

aquí se deja en una EDO lineal, / porque es una de las mejores opciones. Para evaluar este caso, / donde la EDO lineal se tiene que identificar lo que es el / P(t) y Q(t) en este caso. / Queda tal que, / integrar esto, queda tal que e / elevado a k por T. / Y este es mi factor integrante. / Y en este caso me ayudó la IA. La inteligencia artificial me ayudó porque estos dos, al ser constantes, se tienen que agrupar en una sola constante. / y para obtener la C, / que tenemos que encontrarla, / es necesario aplicar la condición inicial. / se encuentra el valor de C y se reemplaza en T(t). / mi C vale 56. / Entonces mi EDO final quedaría / de esta manera. / En donde / esta puede predecir cualquier intervalo de tiempo,

### 6. Estimación de k y validación — Martina Cares (2:46.3–3:13.8 del tramo de voz)

Para calcular cómo se enfría el sistema evaluamos dos modelos matemáticos. En el modelo 1 / se ajustó con dos puntos y utilizó una constante k, / sin embargo, al notar que los residuos que se han de forma sistemática hasta alcanzar los 2 °C / en un tiempo de 30, / revisamos el modelo y así seguimos al segundo modelo, / por regresión con los 16 datos, / que logró un coeficiente de determinación altísimo y redujo el error medio en un 0,4%.

### 7. Propuesta de mejora — Martina Cares (3:13.8–3:40.0 del tramo de voz)

como la constante k depende del área y la conducción del material, servir la leche en un recipiente más ancho o metálico / aumenta la constante / sin gastar energía. / Duplicar k reduce a la mitad / el tiempo para llegar a los 60 °C, / mientras la tasa actual toma / 17,3 minutos al alcanzar esta temperatura / trasladarlo a un recipiente. El recipiente metálico y ancho / nos permite lograrlo tan solo en 8,6 minutos.

### 8. Interpretación — Francisco Carrera (3:40.0–4:23.1 del tramo de voz)

En la interpretación nos quedamos con solamente tres números / que resumen el modelo. El primero es 47 minutos, la constante de tiempo, que es 1 dividido por k, nos dice que cada 47 minutos la diferencia entre la leche y el ambiente se reduce a cerca de un tercio, o sea la leche se enfría más rápido al principio y cada vez mucho más lento. El segundo son los 17 minutos, que es lo que tarda la leche en bajar hasta 60 grados y una temperatura más cómoda para tomarla. / Y el tercero es de 22,1 grados, la temperatura de equilibrio es la temperatura de la habitación, / la leche nunca va a bajar de ahí, solo se va acercando cada vez más lento. En resumen, con un solo valor de k podemos predecir cuánto hay que esperar y hasta dónde llegar el enfriamiento.

### 9. Conclusión — Yeny Zapata (4:23.1–4:43.8 del tramo de voz)

Como conclusión, / tenemos que la ley de Newton describe bien el enfriamiento de la leche, / con un error medio de 0,38 grados Celsius. / Al analizar los residuos, esto nos permitió revisar / y mejorar el modelo. / Sus límites no captan la pérdida rápida inicial ni el efecto aislante de la nata.

## Cortes de contenido (lo que no entra)

| Hablante | Desde → hasta (original) | Duración | Texto | Motivo |
|---|---|---|---|---|
| Adonis | 0:39.9 → 1:06.7 | 26.8 s | Yo estuve a cargo de realizar la experiencia que se realizó el 19 de o … endría siendo nuestro tiempo cero realizando la experiencia. | Toma duplicada de la metodología: se usa la 2ª toma (video_20261110_110535), más completa |
| Adonis | 0:45.6 → 1:02.4 | 16.8 s | Por parte de los roles, el rol que tomé yo fue el de realizar la exper … bservación y análisis, y Vicente por parte de la modelación. | Roles del equipo: recortado por tiempo; los roles se muestran en los lower-thirds |
| Vicente | 0:01.4 → 0:09.5 | 8.1 s | Hola buenas, soy Vicente Acevedo, yo voy a decidir el marco teórico, datos y análisis exploratorio y formulación y resolución. | Autopresentación (la reemplaza el lower-third) |
| Vicente | 0:14.9 → 0:20.5 | 5.6 s | yo trabajé en el modelamento matemático, entonces para este proyecto fue lo principalmente que se usó fue | Muletilla de arranque |
| Vicente | 0:37.1 → 0:57.6 | 20.5 s | Bueno, en este caso, como será una ley de enfriamiento de Newton, se u …  el tiempo, igual a menos la constante, que es la constante, | Explicación trabada de dT/dt (la ecuación se ve en pantalla) |
| Vicente | 1:19.2 → 1:55.4 | 36.3 s | Bueno, en datos y análisis exploratorio, lo que se recalca aquí es el  …  minutos. Corto eso. Es que me voy a explayar más, mejor sí. | Falso comienzo de la sección 4 ("Corto eso… me voy a explayar más") |
| Vicente | 2:18.7 → 2:44.5 | 25.8 s | Y ahora, quiero pasar a la formulación y resolución, que aquí me quier … era ecuación, aquí es donde primero evalué lo que es. Bueno, | Transición / "me quiero explayar" |
| Vicente | 3:05.2 → 3:11.9 | 6.7 s | Al tener P(t) se puede sacar el P(t) se puede sacar el P(t) se puede sacar el P(t), que se evalúa de tal manera que e integral de P(t) de T. | Repetición "se puede sacar el P(t)" ×3 |
| Vicente | 3:22.9 → 4:34.4 | 71.6 s | El factor integrante se evalúa la solución de la lineal, en donde pued … bién, esto fue importante porque yo no supe entenderlo bien. | Detalle algebraico del factor integrante (por tiempo) |
| Vicente | 4:55.9 → 5:17.7 | 21.7 s | La condición inicial es solo tener la T igual a 0, que en este caso es …  la E para el otro lado, y así me quedaría tal cual. Y esto, | Detalle T(0), e^0 = 1 (por tiempo) |
| Vicente | 5:22.1 → 6:00.6 | 38.5 s | Entonces, como dije ahí, aquí encontramos el valor de C y ahora hay qu … T de ambiente del momento inicial. Me queda que tengo que C, | Repetición del reemplazo de C |
| Vicente | 6:04.8 → 7:47.2 | 102.5 s | Esto, claramente se puede resolver. Si reemplazo el T igual 0, se resu … idiendo con el negativo, y me quedaría tal que así. Entonces | Cálculo de k con T(10) = 66,2 (lo explica Martina en la sección 6; se muestra la hoja de procedimiento) |
| Vicente | 7:57.7 → 8:23.0 | 25.4 s | en cualquiera. Lo que ustedes puedan poner, si ustedes prueban, podría … a un aproximado literal con esto. Y así terminaría mi parte. | Invitación a probar con la tabla / cierre |
| Martina | 0:30.4 → 0:34.6 | 4.2 s | Ahora, pasando a la sección 7 de cambiar de recipiente, | Frase de transición (el cambio de sección se ve en pantalla) |

Además se recortaron automáticamente las pausas ≥ 0,35 s dentro de las frases (67 clips en total; margen de 0,12 s a cada lado, crossfade de audio de 30 ms en cada unión). El detalle está en `edl/<hablante>.json`.

## Cifras y frases a revisar (no se editaron)

| Sección | Quién | Lo que se transcribió | Comentario |
|---|---|---|---|
| 6 | Martina | "redujo el error medio **en un 0,4 %**" | El póster y Yeny dan RMSE = 0,38 °C (≈ 0,4 °C, no %). Probablemente dijo "a 0,4" o es error de Whisper; en pantalla se mostrará **RMSE = 0,38 °C** del póster. ¿Lo dejamos así o prefieren recortar "en un 0,4 %"? |
| 6 | Martina | "los residuos que **se han** de forma sistemática hasta alcanzar los **2 °C** en un tiempo de 30" | Audio poco claro ("crecen"/"se van"?). Confirmen que el residuo máximo del Modelo 1 en el póster es ≈ 2 °C a los 30 min. En el subtítulo dejé el texto tal cual se oye. |
| 6 | Martina | "En el modelo 1 **se arrojaron** dos puntos" | Whisper; en el subtítulo lo corregí a "se ajustó con dos puntos". Confirmen. |
| 7 | Martina | "la tasa actual toma **17,3 minutos**" | Francisco y el póster dicen **17 min** (redondeo). Se mantiene la voz; en pantalla manda el póster. |
| 5 | Vicente | k = **0,0238** (hoja y pizarra) | El póster dice 0,0239. El tramo donde lo calcula queda fuera del corte; en pantalla se muestra 0,0239. |
| 2 | Vicente | "la ley de Newton, en donde aquí se evalúa **en** con qué rapidez…" | Titubeo leve en la voz; no se puede cortar sin cortar a mitad de frase. |
| 8 | Francisco | "hasta dónde **llegar** el enfriamiento" | Se oye así (falta "llega"). Sin cambio. |

## Decisiones que necesito que confirmen

1. **Póster:** súbanlo a la carpeta como PDF (ideal) o adjunten la imagen. Sin él no puedo armar los recuadros 3D.
2. **Recorte de Vicente:** su grabación dura 8:26 y el video completo debe durar ≤ 5:00, así que de la sección 5 quedan ~50 s con los pasos clave (EDO lineal → P(t), Q(t) → factor integrante e^{kt} → constantes agrupadas en C → condición inicial → C = 56 → EDO final). Se omite el cálculo de k con T(10) = 66,2: lo explica Martina en la sección 6 y se ve en la hoja de procedimiento. ¿OK?
3. **Roles del equipo** (Adonis, 0:43–1:01 de su 2ª toma) quedan fuera por tiempo, pero se muestran en los lower-thirds con lo que dijo Adonis: Adonis · Experiencia, Yeny · Datos, Francisco y Martina · Observación y análisis, Vicente · Modelación. ¿OK?
4. **Intro:** la tarjeta de título aparece mientras Adonis dice "Hola, somos Adonis, Yeny, Vicente, Francisco y Martina…", y los nombres entran a medida que los nombra. Así ahorramos ~5 s.
5. **Margen:** quedamos en ~4:57. Si quieren más holgura, se pueden sacar "o sea la leche se enfría más rápido al principio y cada vez mucho más lento" (Francisco, ~4 s) y/o "porque es una de las mejores opciones" (Vicente, ~2 s).
6. **Música:** no hay `music.mp3`. ¿La agregan ustedes o sigo sin música?
7. **Hoja de procedimiento:** la captura es tinta de colores sobre fondo oscuro (pizarra digital), no papel blanco. Le aplico realce de contraste/nitidez y escalado ×2 Lanczos, manteniendo el fondo oscuro y montada sobre una tarjeta clara con el estilo del póster.
