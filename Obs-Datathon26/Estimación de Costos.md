## Estimación de Costos Operativos para la Base de Datos `estado_cliente`
*Basado en precios de AWS (US East) actualizados a Abril 2026*

Para estimar el costo operativo se asume que:

(1) ya existe un modelo en producción
(2) la nueva base de datos solo alimentará ese modelo
(3) el pipeline se ejecuta una vez al mes
(4) el procesamiento se realiza con infraestructura cloud estándar

Para esta estimación se usa como referencia **Amazon Web Services (AWS)**.

---

### 1. Cómputo del pipeline
El pipeline está escrito en Python y realiza:
- Extracción desde tres bases de datos.
- Agregación de variables por cliente y periodo.
- Cálculo del estado del cliente.
- Escritura en `estado_cliente`.

**Instancia sugerida:** EC2 `t3.small` (2 vCPU, 2 GB RAM).
- **Costo on-demand:** $0.0208 USD por hora (~$15.18/mes si correra 24/7) .
- **Ejecución mensual:** 30 minutos.
- **Cálculo:** 0.0208 * 0.5 horas = **$0.0104 USD**.
---
### 2. Almacenamiento
La tabla `estado_cliente` almacena el estado por periodo.

**Supuestos:**
- 100,000 clientes
- 24 meses de historial
- 20 variables por cliente

**Volumen:** ~2.4M registros (menos de 1 GB).

**Opción S3 (Recomendada para costos bajos vs. RDS):**
- **Precio S3 Standard:** $0.023 USD por GB/mes.
- **Costo estimado:** $0.023 * 1 GB = **$0.023 USD**.
---
### 3. Monitoreo y logging
Servicio: **Amazon CloudWatch Logs**.

**Costo:**
- **Plan Gratuito:** 5 GB de ingestión, 5 GB de almacenamiento y 1,800 minutos de Live Tail *gratis*.
- **Consumo esperado:** Dado que el pipeline corre una vez al mes, el volumen de logs será mínimo (<< 1 GB).

**Costo mensual estimado:** **$0.00 USD** (Cubre dentro del free tier).

---
### 4. Mantenimiento técnico
El costo dominante. Incluye revisión de ejecuciones, debugging y actualizaciones.

**Tarifa de mercado (Data Engineer):**
- **Latinoamérica / Freelance:** $40 - $60 USD (Rango competitivo).

**Horas mensuales:** 1 – 2 horas.

**Cálculo actualizado:**
- *Caso Low-end:* $50 * 1h = **$50 USD**

---
# Fuentes

1. **EC2 t3.small pricing** - [https://instances.vantage.sh/aws/ec2/t3](https://instances.vantage.sh/aws/ec2/t3) (Precio exacto: $0.0208/hora)
    
2. **S3 Standard storage pricing** - [https://aws.amazon.com/s3/pricing/](https://aws.amazon.com/s3/pricing/) ($0.023 por GB/mes)
    
3. **RDS gp3 storage pricing** - [https://aws.amazon.com/rds/pricing/](https://aws.amazon.com/rds/pricing/) ($0.115 por GB/mes - usado en nota comparativa)
    
4. **CloudWatch Logs free tier** - [https://aws.amazon.com/cloudwatch/pricing/](https://aws.amazon.com/cloudwatch/pricing/) (5 GB ingestión gratis)
    
5. **Data Engineer hourly rate (UK contractor market)** - [https://www.itjobswatch.co.uk/contracts/uk/data%20engineer.do](https://www.itjobswatch.co.uk/contracts/uk/data%2520engineer.do) (Mediana ~£55-70/hora)
    
6. **Data Engineer hourly rate (LatAm / freelance)** - [https://www.glassdoor.com/Salaries/data-engineer-hourly-salary-SRCH_KO0,13.htm](https://www.glassdoor.com/Salaries/data-engineer-hourly-salary-SRCH_KO0,13.htm) (Rango $40-60/hora)
    
7. **EC2 t3.small official pricing** - [https://aws.amazon.com/ec2/pricing/on-demand/](https://aws.amazon.com/ec2/pricing/on-demand/) (Confirmación precio lista $0.0208)
    
8. **CloudWatch Live Tail free tier** - [https://aws.amazon.com/blogs/aws/new-amazon-cloudwatch-live-tail/](https://aws.amazon.com/blogs/aws/new-amazon-cloudwatch-live-tail/) (1,800 minutos gratis)