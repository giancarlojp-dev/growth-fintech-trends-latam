# 🏗️ Arquitectura del Sistema

## Visión General

Este proyecto implementa un pipeline ETL completo para análisis de tendencias fintech en LATAM, con las siguientes capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  Power BI    │      │  Jupyter     │                   │
│  │  Dashboard   │      │  Notebooks   │                   │
│  └──────────────┘      └──────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  Supabase    │◄────►│  CSV Files   │                   │
│  │ (PostgreSQL) │      │  (Processed) │                   │
│  └──────────────┘      └──────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE PROCESAMIENTO                      │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│  │ Extract  │──►│Transform │──►│  Load    │              │
│  │(Pytrends)│   │ (Pandas) │   │(Supabase)│              │
│  └──────────┘   └──────────┘   └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│                    FUENTE DE DATOS                          │
│                                                             │
│              ┌──────────────────────┐                      │
│              │  Google Trends API   │                      │
│              └──────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes del Sistema

### 1. Capa de Extracción

**Responsabilidad:** Obtener datos de Google Trends

**Componentes:**

- `src/extract/google_trends.py`: Lógica de extracción con Pytrends
- `src/config/keywords.py`: Configuración de términos a buscar
- `src/config/countries.py`: Códigos de países LATAM

**Características:**

- Manejo de rate limits (Error 429)
- Reintentos automáticos con backoff exponencial
- Extracción incremental (evita duplicados)
- Logging detallado de operaciones

**Flujo:**

```python
1. Leer configuración (keywords, países)
2. Por cada país:
   3. Por cada keyword:
      4. Verificar si ya existe en DB
      5. Si no existe → Extraer de Google Trends
      6. Guardar en data/raw/
```

---

### 2. Capa de Transformación

**Responsabilidad:** Limpiar y normalizar datos

**Componentes:**

- `src/transform/clean_transform.py`: Funciones de limpieza

**Transformaciones aplicadas:**

- Conversión de tipos de datos (date → datetime)
- Filtrado de valores nulos o inválidos
- Eliminación de scores = 0 (sin interés)
- Cálculo de z-score por grupo (country + keyword)
- Validación de rangos (interest_score: 1-100)

**Ejemplo:**

```python
def clean_transform(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['interest_score'] > 0]  # Filtrar sin interés
    df['z_score'] = df.groupby(['country_code', 'keyword'])['interest_score']\
                      .transform(lambda x: (x - x.mean()) / x.std())
    return df
```

---

### 3. Capa de Carga

**Responsabilidad:** Persistir datos en base de datos

**Componentes:**

- `src/load/supabase_loader.py`: Cliente de Supabase con upsert
- `src/load/fill_missing_data.py`: Detección de gaps y recarga
- `src/load/download_final_dataset.py`: Descarga para validación

**Base de Datos: Supabase (PostgreSQL)**

**Schema:**

```sql
CREATE TABLE fintech_trends (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    keyword TEXT NOT NULL,
    country_code TEXT NOT NULL,
    interest_score INTEGER NOT NULL CHECK (interest_score >= 0 AND interest_score <= 100),
    z_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_entry UNIQUE (date, country_code, keyword)
);
```

**Índices:**

```sql
CREATE INDEX idx_date ON fintech_trends(date);
CREATE INDEX idx_country ON fintech_trends(country_code);
CREATE INDEX idx_keyword ON fintech_trends(keyword);
```

**Operación Upsert:**

```python
client.table('fintech_trends').upsert(
    records,
    on_conflict='date,country_code,keyword'
).execute()
```

---

### 4. Capa Analítica

**Responsabilidad:** Queries y vistas para insights

**Componentes:**

- `sql/views.sql`: Vistas materializadas
- `sql/growth_queries.sql`: Queries de crecimiento

**Vistas Creadas:**

**a) vw_country_avg_interest**

```sql
CREATE VIEW vw_country_avg_interest AS
SELECT
    country_code,
    ROUND(AVG(interest_score), 2) as avg_interest,
    COUNT(*) as total_records
FROM fintech_trends
GROUP BY country_code;
```

**b) vw_keyword_avg_interest**

```sql
CREATE VIEW vw_keyword_avg_interest AS
SELECT
    keyword,
    ROUND(AVG(interest_score), 2) as avg_interest,
    COUNT(DISTINCT country_code) as countries_present
FROM fintech_trends
GROUP BY keyword
ORDER BY avg_interest DESC;
```

---

### 5. Capa de Visualización

**Power BI Dashboard**

**Componentes:**

- `dashboards/fintech_growth_latam.pbix`: Dashboard interactivo
- Fuente de datos: `data/processed/google_trends_final.csv`

**Visualizaciones:**

1. KPI Cards (Total, Países, Periodo)
2. Line Chart (Tendencias temporales)
3. Bar Chart (Comparación por país)
4. Tabla (Top keywords)
5. Slicers (Filtros de fecha y keywords)

**Conexión:**

- Tipo: Import (CSV embebido)
- Actualización: Manual (re-importar CSV si hay nuevos datos)

---

## Flujo de Datos Completo

```
┌──────────────┐
│ Google Trends│
│     API      │
└──────┬───────┘
       │ GET /trends/explore
       ▼
┌──────────────┐
│  Pytrends    │ ← src/extract/google_trends.py
│  Extraction  │
└──────┬───────┘
       │ Save CSV
       ▼
┌──────────────┐
│ data/raw/    │ ← google_trends_master.csv
│  Raw Data    │
└──────┬───────┘
       │ Read & Transform
       ▼
┌──────────────┐
│   Pandas     │ ← src/transform/clean_transform.py
│ Cleaning     │
└──────┬───────┘
       │ Upsert
       ▼
┌──────────────┐
│  Supabase    │ ← PostgreSQL Database
│  PostgreSQL  │
└──────┬───────┘
       │ Download & Validate
       ▼
┌──────────────┐
│data/processed│ ← google_trends_final.csv
│ Final Dataset│
└──────┬───────┘
       │ Import
       ▼
┌──────────────┐
│  Power BI    │ ← Dashboard interactivo
│  Dashboard   │
└──────────────┘
```

---

## Patrones de Diseño Aplicados

### 1. Idempotencia

**Problema:** Reejecutar el pipeline genera duplicados

**Solución:**

- Constraint UNIQUE en base de datos
- Operación UPSERT (insert or update)
- Verificación previa antes de extraer

### 2. Retry Pattern

**Problema:** API de Google Trends bloquea con Error 429

**Solución:**

```python
for attempt in range(max_retries):
    try:
        data = pytrends.interest_over_time()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

### 3. Separation of Concerns

**Problema:** Código monolítico difícil de mantener

**Solución:**

- Carpetas separadas: extract/, transform/, load/
- Cada módulo con responsabilidad única
- Configuración separada del código

### 4. Data Validation

**Problema:** Datos corruptos o inconsistentes

**Solución:**

- Notebook de validación (02_validation.ipynb)
- Comparación CSV local vs Base de datos
- Checks de integridad (nulls, tipos, rangos)

---

## Escalabilidad

### Actual (1,635 registros)

- Todo en memoria (Pandas)
- CSV como respaldo
- PostgreSQL para persistencia

### Futuro (>100k registros)

- Migrar a Apache Spark para procesamiento
- Usar Parquet en lugar de CSV
- Implementar data partitioning por país/año
- Airflow para orquestación de pipeline

---

## Seguridad

**Credenciales:**

- Almacenadas en `.env` (excluido de Git)
- Cargadas con `python-dotenv`
- Nunca hardcodeadas en código

**Base de Datos:**

- Row Level Security (RLS) en Supabase
- API keys con permisos limitados
- Conexión SSL/TLS

---

## Monitoreo y Logs

**Logging:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Extrayendo datos para PE - Yape")
logger.warning("Rate limit alcanzado, reintentando...")
logger.error("Falló extracción para keyword X")
```

**Métricas actuales:**

- Total de registros extraídos
- Tiempo de ejecución del pipeline
- Tasa de éxito/fallo por keyword

---

## Tecnologías y Versiones

```
Python: 3.11+
Pandas: 2.0+
Pytrends: 4.9+
PostgreSQL: 15+ (vía Supabase)
Power BI Desktop: Última versión
```

_Última actualización: Marzo 2026_
