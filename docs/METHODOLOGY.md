> **⚠️ Advertencia Importante:**
>
> En los datos proporcionados para el ejercicio se identificó un **error en las fechas** de estos. Existen **variaciones de precios en días no hábiles** (cómo los días sábado). Se asume que en la extracción de los datos, pudo haber habido un error en el formateo de fechas derivado de una diferencia en la zona horaria lo que hizo que las fechas rezagaron un periodo hacia adelante.
>
> Para incluir variables exógenas y, dado que se trata de una serie de tiempo, es que se determinó rezagar de la misma forma las variables exógenas utilizadas para no interferir en la comprensión de la serie original.

## **Especificación Econométrica**

El modelo de regresión lineal utilizado en este proyecto está definido de la siguiente manera:

$$
\hat{\Delta \ln(USD\_CLP_{t+i})} =
f(\mathbf{X}_{t-j}, \boldsymbol{\theta}_i) + \varepsilon_t,
\quad \text{donde } i \in \{1, 2, 3\}
$$

**Donde:**

$$
\Delta \ln(USD\_CLP_{t+i}) \equiv \ln(USD\_CLP_{t+i}) - \ln(USD\_CLP_{t+i-1}),
$$

y cada $\boldsymbol{\theta}_i$ corresponde a modelos independientes para cada horizonte de predicción ($t+i$).

Para llevar el retorno predicho a valor monetario, se utiliza la siguiente fórmula:

$$
USD\_CLP_{t+i} = \frac{USD\_CLP_t}{1 + \hat{\Delta \ln(USD\_CLP_{t+i})}}
$$

**Descripción de los Componentes:**

- **$\hat{\Delta \ln(USD\_CLP_{t+i})}$:** Retorno logarítmico predicho para el tipo de cambio en el periodo $i$ días adelante.
- **$\mathbf{X}_{t-j}$:** Vector de variables explicativas que incluye:
  - Los dos primeros rezagos del retorno diario del tipo de cambio ($j \in \{0, 1\}$).
  - Los cuatro primeros rezagos del retorno diario del precio del cobre ($j \in \{0, 1, 2, 3\}$).
- **$\boldsymbol{\theta}_i$:** Vector de parámetros específicos para cada horizonte de predicción.
- **$\varepsilon_t$:** Término de error del modelo.

## **Resultados Fuera de Muestra**

A cotinuación se presentan el resumen de la distribución de errores para la especificación que incluye componente autoregresiva de orden 2 AR(2) y 4 rezagos del cobre.

### COPPER(2,4)

| step_ahead | count  | mean     | std      | min      | 25%      | 50%      | 75%       | max        |
| ---------- | ------ | -------- | -------- | -------- | -------- | -------- | --------- | ---------- |
| 1          | 1405.0 | 4.339783 | 4.793274 | 0.001015 | 1.314538 | 3.014086 | 5.796894  | 63.516765  |
| 2          | 1404.0 | 7.332586 | 7.398158 | 0.019956 | 2.446569 | 5.619880 | 10.151884 | 117.387614 |
| 3          | 1402.0 | 9.662634 | 9.085992 | 0.004819 | 3.564567 | 7.568629 | 13.358626 | 132.966236 |

Los valores representan los errores en Pesos Chilenos (CLP).

En resumen para las predicciones 1 paso hacia adelante en promedio la desviación es de CLP$4.34, mientras que la mediana se ubica en CLP$3.01, donde existe un claro impacto de outliers a la derecha de la distribución. Por su parte, las predicciones en los pasos 2 y 3 muestran un aumento en los errores a CLP$7.39 y CLP$9.66 en sus respectivos promedios. Misma situación ocurre en la mediana y outliers positivos.

## **Futuros Pasos**

1. Corrección base de datos tipo de cambio. Es importante contar con la certeza de que los datos no han sido manipulados ni alterados en sus fechas.
2. Derivado del posible error en la base de datos es que los precios del cobre podrían no estar alineados en fecha con el de tipo de cambio. Es importante asegurar la calidad de la extracción y consistencia en los datos.
3. Variables Exógenas. Si bien uno de los fundamentales del tipo de cambio del peso chileno es el precio del Cobre, existen otras variables que podrían perturbar o influir en la serie, como lo es la Tasa de Política Monetaria. Experimentar e incluir esta variable podría corregir ciertos outliers que sesgan el cálculo de los estimadores del modelo.
4. Para efectos del ejercicio solo se probó con un modelo lineal (Regresión Lineal Multiple) en diferentes especificaciones económetricas y horizontes de predicción. Sería interesante como se comportan otros modelos de regresión (Support Vector Regressor, por ejemplo) en estos casos.
5. Dado la naturaleza de la serie, donde se existen periodos de alta y baja volatilidad (incertidumbre), es que sería interesante modelar esta volatilidad a través de un modelo GARCH.
