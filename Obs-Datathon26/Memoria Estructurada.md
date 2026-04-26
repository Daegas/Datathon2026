Hey Banco es servicio digital para manejar los recursos económicos de un usuario

Promedio de **7.5** de satisfacción. 
Un 7.5 es aprobatorio, pero se puede mejorar.


![[Pasted image 20260426004814.png]]
---
---

# En Búsqueda de la Satisfacción

*¿Qué es aquello que hey banco puede ajustar, ofrecer para aumentar de manera personalizada la satisfacción de un **cliente**?*

Antes que eso, 
### **¿ Qué define a un [[Usuario]]?**

---
#  Propuesta y Happy Path 

Registro reducido histórico con actualización mensual ([[#Mejoras]]) del cliente. 
En otras palabras un matcheo periódico de estado del cliente con satisfacción.

---
# Objective Workflow
[[Flow Diagram.canvas]]

---
# ¿Y cómo nos ayuda *yet another* table?
$$\text{estadocliente}(t)= f(\text{satisfaccion}, \text{comportamiento}, \text{productos}, \text{transacciones})$$

Esto permite:
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

## Feature Engineering
[[Productos]]
[[Transacciones]]
[[Conversaciones]]

---
# Escalabilidad
## Etapa de Desarrollo
Investigación de lógica del estado del cliente
## Etapa de Implementación
Todo el código está hecho en python, tratando de usar convenciones pero al final se puede implementar un pipeline que corra automáticamente cada mes que vaya populando la DB en backend y sea usado en el modelo final.

---
# [[Estimación de Costos]]

---
# Mejoras

* **Periodicidad:** Podría ser otro punto de ajuste  a gusto de la compañia y límitado por el poder de cómputo, se puede hacer en paralelo dependiendo de la necesidad
* **Estatus de [[Productos]]:** Definir más niveles 
	* tiene 
	* no tiene 
	* podría querer (agregar)
	* quiere (agregar)
* Mejorar el modelo del pseudo-havi no está directamente en el goal, pero si hacer una comparación de contexto vs. no contexto. (A/B testing)

----


> [[Uso de IA]]: Algunos archivos (o subarchivos) tienen en la parte de abajo el chat



 


