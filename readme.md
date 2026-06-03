# ✂️ Universal Sprite Slicer & Cutter Pro

Una herramienta visual e inteligente construida en Python para desarrolladores de videojuegos y artistas técnicos. Permite trocear, separar y exportar hojas de sprites (*spritesheets*) de forma masiva o manual en cuestión de segundos.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---
<img width="1920" height="1080" alt="{1780BE26-2B6E-4ED1-9664-2FC4A7FB5CE0}" src="https://github.com/user-attachments/assets/550a4d2d-722e-4cb7-a1df-1d7315d7a2a2" />

## ✨ Características Principales

* **🖱️ Modo Manual Dinámico:** Haz clic y arrastra el ratón sobre cualquier formato de imagen (`PNG`, `JPG`, `BMP`, `TGA`) para recortar regiones personalizadas al instante.
* **⚙️ Modo Automático Inteligente:** Algoritmo avanzado de detección de subpíxeles basado en inundación (*Flood Fill*) que aísla y calcula cajas delimitadoras automáticas en imágenes `PNG` con fondo transparente.
* **🎚️ Tolerancia de Agrupación Ajustable:** Controla mediante un deslizador (*slider*) la distancia en píxeles para fusionar islas de color cercanas (ideal para personajes con accesorios flotantes o piezas separadas).
* **🎯 Nomenclatura Incremental Directa:** Exporta tus recortes automáticamente evitando colisiones de archivos. Si guardas como `monstruo`, el sistema creará `monstruo1.png`, `monstruo2.png`, etc, detectando archivos para no sobreescribir por nombre.
* **🧵 Interfaz Asíncrona (Multihilo):** El procesamiento pesado de imágenes y las exportaciones masivas corren en hilos secundarios. La interfaz gráfica nunca se congela ni se bloquea.
* **⏱️ Interfaz Limpia:** Mensajes de estado inteligentes y temporizados para mantener tu espacio de trabajo impecable y libre de distracciones.

---

## 🚀 Instalación Automática (Zero Setup)

¡Se acabaron las peleas con la terminal! El script cuenta con un **sistema de despliegue automatizado** mediante una ventana de carga integrada (*Splash Screen*).

Al ejecutar `cutter.py` por primera vez:
1. Una micro-ventana comprobará si tienes instaladas las dependencias requeridas (`customtkinter` y `pillow`).
2. Si falta alguna, **las descargará e instalará de fondo de forma silenciosa e invisible**.
3. Una barra de progreso fluida te mantendrá informado. Una vez completado, el entorno se refrescará por sí solo y lanzará la aplicación directamente.

---

## 🛠️ Requisitos Previos

Solo necesitas tener instalado **Python 3.10 o superior** en tu sistema operativo y asegurarte de tener conexión a Internet la primera vez que abras el programa para que actúe el auto-instalador.

Si por algún motivo prefieres instalar las librerías a mano, puedes abrir tu terminal y ejecutar:
```bash
pip install customtkinter pillow
```


## 📖 Cómo Usar la Aplicación
Importar la imagen: Pulsa el botón 1. Importar Imagen y selecciona tu hoja de sprites.

Nombrar tus assets: Escribe el prefijo que quieras en el cuadro de texto (por ejemplo: enemigo_orco).

Elegir tu método de corte:

Si es un PNG transparente: Activa el interruptor “Ver Previsualización Auto”. Ajusta la Tolerancia de Agrupación hasta que las cajas verdes envuelvan correctamente tus objetos y pulsa “Guardar Todo el Autocorte”.

Si es una imagen opaca (o quieres un recorte específico): Haz clic izquierdo en el lienzo y arrastra el ratón sobre el sprite deseado. Al soltarlo, se guardará inmediatamente de forma manual.

Recoger tus archivos: Abre la carpeta local assets_recortados/ que se habrá generado al lado de tu script para encontrar todos tus sprites individuales listos para usar en tu motor de videojuegos favorito (Unity, Godot, Unreal, etc.).


🤝 Contribuciones
Las contribuciones, reportes de fallos (issues) y sugerencias son más que bienvenidos. Siéntete libre de revisar la sección de issues o abrir un pull request para mejorar el algoritmo de detección o añadir nuevas funciones a la interfaz.


📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo de licencia para más detalles.


Desarrollado con 💙 por Aisurf3r para la comunidad de desarrollo de videojuegos independientes.
