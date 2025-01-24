# Modelo de Predicción Tipo de Cambio USD/CLP

Este repositorio contiene un modelo de predicción diseñado para estimar el tipo de cambio entre el Dólar Estadounidense (USD) y el Peso Chileno (CLP) con un horizonte de tres días. El modelo utiliza técnicas de regresión lineal aplicadas a series de tiempo.

Para más detalles de la metodologia ver [`Metodología`](src/METHODOLOGY.md)

## Instrucciones de Ejecucion:

**1. Clonar repositorio**

```bash
git clone https://github.com/ignacioTapia95/forecast-usd-clp-exchange-rate
cd forecast-usd-clp-exchange-rate
```

**2. Crear y activar entorno virtual**

- Unix

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- Windows
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Ejecutar modelo**

> ⚠️ **Nota importante:**
>
> La primera ejecución del modelo puede tomar más tiempo de lo esperado debido a la inicialización de dependencias, carga del modelo o preparación de datos. Las ejecuciones posteriores serán significativamente más rápidas.

```bash
python main.py --last-train-date "[YYYY-MM-DD]" --confidence-level 0.95
```

Reemplaza `[YYYY-MM-DD]` con las fecha de corte deseada para el entrenamiento. Considera que hasta esta fecha se ajustará el modelo y las predicciones se harán en t+1, t+2 y t+3

Ejemplo:

```bash
python main.py --last-train-date "2024-10-24" --confidence-level 0.95
```

Generará las predicciones para las siguientes fechas:

- 2024-10-25
- 2024-10-26
- 2024-10-27

Si la fecha introducida no es un día hábil, esta se ajustará para el ultimo día hábil disponible. Lo mismo ocurre para las fechas de predicción, es decir, si la fecha a predecir no es un dia hábil, se reemplazará por el día hábil más próximo.

## Ejemplo de Output:

```json
{
  "current_date": "2024-10-24",
  "forecast": {
    "t+1": {
      "date_t+1": "2024-10-25",
      "usd_t+0": 951.0,
      "usd_forecast": 951.3686953063227,
      "usd_forecast_confidence": {
        "confidence_level": 0.95,
        "interval": [938.2832310267347, 964.4541595859104]
      },
      "usd_observed": "None",
      "variation_forecast": 0.00038769222536550157,
      "variation_observed": "None"
    },
    "t+2": {
      "date_t+2": "2024-10-26",
      "usd_t+0": 951.0,
      "usd_forecast": 952.4584555122709,
      "usd_forecast_confidence": {
        "confidence_level": 0.95,
        "interval": [931.891816943982, 973.02509408056]
      },
      "usd_observed": "None",
      "variation_forecast": 0.0015336020108001852,
      "variation_observed": "None"
    },
    "t+3": {
      "date_t+1": "2024-10-29",
      "usd_t+0": 951.0,
      "usd_forecast": 953.1759464526586,
      "usd_forecast_confidence": {
        "confidence_level": 0.95,
        "interval": [926.9369817457606, 979.4149111595565]
      },
      "usd_observed": "None",
      "variation_forecast": 0.0022880614644149293,
      "variation_observed": "None"
    }
  }
}
```

| Concepto                  | Definicion                                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `current_date`            | Última fecha utilizada para el entrenamiento                                                                              |
| `date_t+i`                | Fecha correspondiente al dia predicho                                                                                     |
| `usd_t+0`                 | Valor Real del Tipo de Cambio en la ultima fecha de entrenamiento                                                         |
| `usd_forecast`            | Valor predicho para `date_t+i`                                                                                            |
| `usd_forecast_confidence` | Intervalo de confianza del valor del dolar predicho para `date_t+i`                                                       |
| `usd_observed`            | Valor Real del Tipo de cambio en `date_t+i`. En caso de no haber información sobre `date_t+i`, este valor será `None`     |
| `variation_forecast`      | Variación predicha del Tipo de Cambio en `date_t+i`.                                                                      |
| `variation_observed`      | Variación Real del Tipo de cambio en `date_t+i`. En caso de no haber información sobre `date_t+i`, este valor será `None` |
