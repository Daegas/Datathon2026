# En Búsqueda de la Satisfacción

Promedio actual: 7.5

*¿Cómo aumentar de manera personalizada la satisfacción de un **cliente**?*

Antes que eso, 
### **¿ Qué define a un [[Usuario]]?**

---
#  Propuesta y Happy Path 

Registro reducido histórico con actualización periódica del estado del cliente. 

---
# Objective Workflow
[[Flow Diagram.canvas]]

---
# ¿Para qué?

Permite resumir datos dispersos en varios sistemas en una señal simple que muestra cómo está el cliente en cada momento a lo largo del tiempo
## Decisiones personalizadas

Advantages:
* Ver evolución de la relación con el cliente
* Detectar riesgo u oportunidades
*  Product Insight
	- qué productos generan más satisfacción?
	- qué eventos bajan la satisfacción?
	- qué tipo de interacción con el bot mejora la relación?
- Análisis de eventos, adquisión de producto

Esta base de datos serviría como contexto de un usuario al modelo que actualmente usa HAVI

---
# [[Resultados]]
[[Flow Diagram.canvas]]

## Estado de clientes
[[Productos]]
[[Transacciones]]
[[Conversaciones]]

## Resultado
[[HAVI]]

---
# Escalabilidad

* Un único procesamiento hacia atras
* Después el cálculo del estado del cliente se puede automatizar mediante un pipeline que procese periódicamente los datos de las distintas bases y agregue un nuevo registro por cliente y periodo. 
* Con el paso del tiempo se necesita más almacenamiento que se puede manejar con un servicio en la nube como S3

---
# [[Estimación de Costos]]


| Rubro              | Descripción                     | Costo mensual estimado |
| :----------------- | :------------------------------ | :--------------------- |
| **Cómputo**        | EC2 t3.small (30 min mensuales) | $0.01 USD              |
| **Almacenamiento** | S3 Standard (1 GB)              | $0.02 - $0.10 USD      |
| **Monitoreo**      | CloudWatch (Free Tier)          | $0.00 USD              |
| **Mantenimiento**  | Ingeniería (1-2 horas)          | $50 - $100 USD         |

**Costo total estimado:**
Para 100,000 clientes $50.3 – $110.1 USD por mes

---
# Mejoras

* Optimización del modelo que define el **estado del cliente**
* A/B Testing  con benchmarking con un el modelo de Havi.
* **Periodicidad:** Podría ser otro punto de ajuste  a gusto de la compañia y límitado por el poder de cómputo, se puede hacer en paralelo dependiendo de la necesidad
* **Estatus de [[Productos]]:** Definir más niveles 
	* tiene 
	* no tiene 
	* podría querer (agregar)
	* quiere (agregar)

----


> [[Uso de IA]]: Algunos archivos (o subarchivos) tienen en la parte de abajo el chat



 


