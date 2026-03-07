# Analista de Vacantes + ChatGPT

Este proyecto es una aplicación web moderna diseñada para automatizar la extracción de requisitos en ofertas de trabajo y proporcionar análisis estratégicos mediante Inteligencia Artificial (OpenAI GPT).

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.0-orange.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-purple.svg)

## Características Principales

- **Scraping Automatizado**: Utiliza Selenium y BeautifulSoup para navegar y extraer información en tiempo real de vacantes públicas en LinkedIn.
- **Análisis con IA (On-Demand)**: Genera resúmenes profesionales, stacks tecnológicos y niveles de experiencia requeridos usando la API de OpenAI solo cuando el usuario lo solicita.
- **Exportación Multi-formato**: Permite descargar los datos extraídos en formatos **JSON** y **Excel (XLSX)** para un análisis posterior.
- **Arquitectura Limpia**: Código organizado bajo principios SOLID y patrones de diseño (**Estrategia, Fábrica y Fachada**).
- **Interfaz Web Moderna**: Interfaz responsiva con **Modo Oscuro** (Dark Mode) construida con Flask, HTML5, CSS3 y JavaScript.

## Stack Tecnológico

- **Backend**: Python 3.13 + Flask
- **Scraping**: Selenium, WebDriver Manager, BeautifulSoup4
- **Procesamiento de Datos**: Pandas, Openpyxl
- **IA**: OpenAI API (GPT-3.5/4)
- **Frontend**: HTML5, CSS3 (Custom Dark Theme), JavaScript (Fetch API)

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- Python 3.10 o superior.
- Google Chrome instalado (para el Webdriver).
- Una cuenta de OpenAI con una API Key activa.

## Instalación y Configuración

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/webscraping_linkedin.git](https://github.com/tu-usuario/webscraping_linkedin.git)
   cd webscraping_linkedin
   
2. **Instala las dependencias:**
   pip install -r requirements.txt

3. **Configura las variables de entorno:**
   OPENAI_API_KEY=tu_clave_aqui

## Uso
1. **Inicia el servido Flask:**
   python flask_app.py

2. **Accede a la aplicación:**
   Abre tu navegador en http://127.0.0.1:5000

3. **Busca una vacante:**
   Ingresa el puesto deseado (ej. "Frontend Developer") y presiona "Extraer Datos".

4. **Genera el resumen:**
  Una vez completada la extracción, presiona el botón "Generar Resumen Estratégico" para activar la IA.

## Estructura del Proyecto
- **scraping/**: Lógica de navegación y extracción (Patrón Estrategia).
- **logica_negocio/**: Orquestador principal del sistema (Patrón Fachada).
- **inteligencia_artificial/**: Integración con la API de OpenAI.
- **exportadores/**: Lógica para generar archivos Excel y JSON (Patrón Fábrica).
- **static/ & templates/**: Archivos del frontend (CSS, JS y HTML).
- **utilidades/**: Herramientas de limpieza de texto y filtrado.

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
