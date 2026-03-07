    // Variables globales para guardar los datos entre peticiones
    let tituloActual = "";
    let habilidadesActuales = [];

    async function buscarOferta() {
        const puesto = document.getElementById('puesto-input').value;
        if (!puesto) {
            alert("Por favor, ingresa un puesto a buscar.");
            return;
        }

        // Actualizar UI a estado de carga
        document.getElementById('status-text').innerText = "⏳ Extrayendo datos de LinkedIn (Esto puede tardar unos segundos)...";
        document.getElementById('btn-buscar').disabled = true;
        document.getElementById('btn-buscar').innerText = "Cargando...";
        document.getElementById('btn-ia').classList.add('hidden');
        document.getElementById('downloads-container').classList.add('hidden');
        document.getElementById('ai-output').innerHTML = "El análisis de la vacante aparecerá aquí una vez que lo solicites...";

        try {
            // Llamada POST a nuestra ruta de Flask usando FormData
            const formData = new FormData();
            formData.append('puesto', puesto);

            const response = await fetch('/buscar', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.exito) {
                // Guardar variables globalmente para la IA
                tituloActual = data.titulo_oferta;
                habilidadesActuales = data.habilidades;

                // Actualizar Textos
                document.getElementById('status-text').innerText = "✅ ¡Proceso completado con éxito!";
                document.getElementById('titulo-text').innerText = tituloActual;

                // Actualizar Tabla de Habilidades
                const tbody = document.getElementById('skills-body');
                tbody.innerHTML = ""; // Limpiar tabla
                data.habilidades.forEach(hab => {
                    tbody.innerHTML += `<tr><td>${hab}</td></tr>`;
                });

                // Mostrar botón de IA
                document.getElementById('btn-ia').classList.remove('hidden');

                // Configurar y mostrar botones de descarga (Asumiendo que Flask devuelve las rutas)
                // Se busca el nombre del archivo de las rutas generadas
                if (data.rutas_archivos) {
                    const jsonPath = data.rutas_archivos.find(r => r.endsWith('.json'));
                    const excelPath = data.rutas_archivos.find(r => r.endsWith('.xlsx'));
                    
                    if(jsonPath) {
                        const jsonName = jsonPath.split('/').pop();
                        document.getElementById('download-json').href = `/descargar/${jsonName}`;
                    }
                    if(excelPath) {
                        const excelName = excelPath.split('/').pop();
                        document.getElementById('download-excel').href = `/descargar/${excelName}`;
                    }
                    document.getElementById('downloads-container').classList.remove('hidden');
                }

            } else {
                document.getElementById('status-text').innerText = `❌ Error: ${data.error || 'Desconocido'}`;
            }
        } catch (error) {
            document.getElementById('status-text').innerText = "❌ Error de conexión con el servidor.";
            console.error(error);
        } finally {
            // Restaurar botón
            document.getElementById('btn-buscar').disabled = false;
            document.getElementById('btn-buscar').innerText = "🔍 Extraer Datos";
        }
    }

    async function generarResumenIA() {
        if (!tituloActual || habilidadesActuales.length === 0) return;

        const aiOutput = document.getElementById('ai-output');
        const btnIa = document.getElementById('btn-ia');

        // Actualizar UI
        aiOutput.innerHTML = "<em>⏳ Consultando a ChatGPT... Por favor espera.</em>";
        btnIa.disabled = true;

        try {
            // Enviar datos como JSON a Flask
            const response = await fetch('/analizar_ia', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    titulo: tituloActual,
                    habilidades: habilidadesActuales
                })
            });

            const data = await response.json();

            // Usar la librería marked.js para convertir el Markdown de GPT a HTML bonito
            if(data.resumen) {
                aiOutput.innerHTML = marked.parse(data.resumen);
            } else {
                aiOutput.innerHTML = `❌ Error: ${data.error || 'No se pudo generar el resumen.'}`;
            }

        } catch (error) {
            aiOutput.innerHTML = "❌ Error de conexión al generar resumen.";
            console.error(error);
        } finally {
            btnIa.disabled = false;
        }
    }