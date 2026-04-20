# Objetivo

1) Crear un agente que busque noticias de empresas sobre las que quiero conocer las últimas noticias. Por lo tanto el agente debera navegar en webs proporcionadas en busca de noticias sobre dichas empresas

# Especificaciones

1) tengamos herbie_llm.py como el fichero con el que nos conectamos a los llms
2 crear un fichero nuevo (notebook si se puede) que contenga agente lalmado "agente_busqueda_noticias"
3) utiliza los últimos avances de langchain (pero sin usar langgraph todavía si es posible)

# fichero de entrada

1) El excel de entrada se llama URLs.xlsx que tiene dos columnas "url" y "comentario", por ahora trabajaremos solo con la columna "url"

# pantalla

1) tiene que tener una caja de texto en la que se me pida el nombre de la empresa a buscar.
2) tiene que tener un combo que elija el modelo (o varios combos si necesitas más modelos para diferntes tareas)

# proceso

1) Por pantalla introduzco el nombre de la empresa
2) se tiene que recorre la columna "url" y por cada web que aparezca navegar buscando noticias de la empresa
3) se mostrará un listado de las noticias con el titular, y una breve descripción con posibilidad de empliar a ver la noticia entera
4) se analizará el sentimiento de la noticia y se mostrará junto al título
5) se mostrará la fecha de la noticia junto al título en formato dd/mm/yyyy

# Preguntas

no hagas nada, solo dime como lo harías repondiendo a las siguientes preguntas:

- ¿cómo propones hacer la navegación? ¿selenium? ¿dime alternativas?

# añadir navegación

- Ahora quiero añadir la funcionalidad de poder navegar dentro de la página web para conseguir un objetivo
- para ellos añade a la izquierda la capacidad de elegir que modelo usar entre los que tenemos disponibles dne herbie_llm.py
- crea otro input para añadir "objetivo" créalo de 3 líneas para que tenga espacio de escribir. Aquí le daré el promppt del objetivo por ejemplo "descarga el texto de una columna de opinión de john doe" o "descarga el fichero donde la empress uber publica sus annual reports"
- para ello el modelo tendrá que razonar sobre qué tiene que usar para ellos
- la herramienta a crear de navegación creala con playwright para aprovecar el html que ya tenemos la habilidad de descargar
- para ello, adapta el proces de búsqueda actual para que con el mimo html que ya tenemos moentado en función de si lo que estoy haciendo es buscar u texto (funcionalidad actual) o clumplir un objetivo (funcionalidad a implementar)
- Respeta en la medida de lo posible los comentarios que he puesto y sigue esa misms línea de comentarios en lo que hagas

dime como lo implementarias, no lo hagas todavía


Nuevas

- en "herbie_app.py" quiero crear un tercer modo llamado "Cerebro"
- Este cerebro se conectará a una wiki situada en "'/Users/javierzazo/Library/CloudStorage/GoogleDrive-javizzdz76@gmail.com/Mi unidad/context/ProyectoCerebro/wiki'"
- Esta wiki está creada con este paradigma "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"
- como implementarías que el herbie pueda acceder a ese contexto con el paradigma expresado por larpathy para poder reducir los tokens necesarios en su consulta?