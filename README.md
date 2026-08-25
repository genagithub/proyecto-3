### 💼 Sistema Interactivo de Control Financiero y Dimensiones de Negocio

#### 🎯 El Contexto del Problema 
La gerencia comercial de AdventureWorks opera bajo un baseline financiero global aceptable, pero carece de visibilidad atómica sobre la rentabilidad real de sus operaciones durante los cierres mensuales. Al consolidar el tramo correspondiente al mes de junio, el equipo de ventas y operaciones se enfrenta a una profunda incertidumbre provocada por la dispersión de sus datos relacionales, los cuales ocultan el impacto real de los costos de flete, impuestos y producción detrás de los ingresos brutos superficiales. Ante la falta de un flujo integrado, la organización requiere con urgencia centralizar estas fuentes fragmentadas para aislar las ineficiencias logísticas interregionales, identificar con precisión el comportamiento de sus clientes de alto valor y determinar la verdadera eficiencia de su estrategia omnicanal antes de que concluya el ciclo operativo.

---

#### 🛠️ Solución Técnica: Arquitectura e Integración
Se desarrolló un pipeline local migrado a un entorno portátil que centraliza la información de forma eficiente. Mediante el uso de Python (Host) y SQL, se procesaron las transacciones directamente en el motor de la base de datos para garantizar la integridad y velocidad del flujo:
- **Consultas Avanzadas de Integración Dimensional:** Uso de CTEs y uniones relacionales optimizadas para consolidar las tablas de hechos de ventas con los catálogos de productos, territorios y clientes en un único entorno portátil.
- **Extracción de KPIs Medainte Funciones de Agregación :** Modelado matemático y financiero de márgenes netos reales, costos logísticos prorrateados y líneas de base globales ejecutados directamente en el servidor para evitar la sobrecarga de memoria.
- **Segmentación Dinámica de Entidades:** Implementación de lógicas condicionales y filtros que permiten aislar el comportamiento individual de los compradores de alto valor frente a la eficiencia de la estrategia omnicanal o rentabilidad de categorías.
     
---

#### 🚀 Solución Analítica: Panel de Control Financiero por DIMs
El resultado es una herramienta interactiva que traduce las relaciones realizadas en visualizaciones dinámicas cruzadas que permiten monitorear los indicadores críticos de rendimiento comercial junto con la observación de promedios globales y la comparación directa con las palancas de negocio de cada dimensión: 
- **Evaluación de Rentabilidad por Categoría:** Visualización agrupada de ingresos y ganancias netas que expone la anatomía de costos de cada línea de productos, revelando qué clases sostienen la caja del negocio.
- **Monitoreo Omnicanal y Territorial:** Gráficos cruzados por país y canal de distribución que permiten aislar ineficiencias logísticas y comparar de forma instantánea el rendimiento de la tienda física frente al e-commerce.
- **Analítica de Clientes VIP de Alto Valor:** Panel de segmentación individualizado que destaca a los usuarios de mayor gasto y frecuencia de compra, facilitando la creación de estrategias dirigidas a maximizar la retención.


---

#### 📌 Propósito de este Proyecto: Impacto Financiero 
**Eficiencia, Transparencia y Rentabilidad:** Optimiza la toma de decisiones gerenciales al visibilizar los márgenes netos reales y aislar las ineficiencias de costos del mes, transformando la incertidumbre de los datos en palancas estratégicas de crecimiento financiero.
