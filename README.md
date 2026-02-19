# 🚀 Growth Fintech Trends LATAM

Este proyecto analiza la adopción y crecimiento de tendencias Fintech en Latinoamérica (Perú, Colombia, México, Chile) utilizando datos de **Google Trends**.

## 🎯 Objetivo
Identificar patrones de interés en términos clave como "Billetera Digital", "Neobanco", "Criptomonedas", "Yape", "Plin", entre otros, para entender la evolución del mercado financiero digital en la región.

## 🛠️ Tecnologías
- **Python**: Lenguaje principal.
- **Pytrends**: Extracción de datos de Google Trends.
- **Pandas**: Limpieza y manipulación de datos.
- **Matplotlib/Seaborn**: Visualización de datos (EDA).
- **SQLAlchemy/PostgreSQL**: (En progreso) Almacenamiento de datos.

## 📂 Estructura del Proyecto
- `src/extract`: Scripts para la extracción robusta de datos (manejo de errores 429, reintentos).
- `src/transform`: Limpieza y normalización de dataframes.
- `notebooks`: Análisis Exploratorio de Datos (EDA).
- `data/raw`: Datos crudos extraídos.

## 💡 Desafíos Superados
- Implementación de un sistema de **extracción incremental** para evitar duplicados.
- Manejo automático de **bloqueos de API (Error 429)** con retries y backoff exponencial.
- Estructuración modular del código siguiendo buenas prácticas de Ingeniería de Datos.
