import os
import sys
import pandas as pd
import numpy as np

# fmt: off
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.utils import is_business_day
from lib.exog_data import get_yfinance_data
# fmt: on


def preprocessor(df: pd.DataFrame, market_calendar) -> pd.DataFrame:
    """
    Preprocesa un DataFrame para preparar datos de series de tiempo, enfocándose en la variable 'usd_clp' y
    enriqueciendo con información de precios del cobre.

    El proceso de preprocesamiento incluye las siguientes etapas:

    1. **Conversión y ordenamiento de fechas:**
       - Convierte la columna 'dates' a formato datetime.
       - Ordena el DataFrame por fechas de manera ascendente.

    2. **Renombramiento de columnas:**
       - Renombra la columna 'iata' a 'usd_clp' para reflejar correctamente la variable de interés.

    3. **Filtrado de días hábiles:**
       - Utiliza un calendario de mercado cambiario proporcionado para identificar y mantener solo los días hábiles.
       - Elimina los días no hábiles para evitar errores en el cálculo de estimadores.

    4. **Creación de variables rezagadas y adelantadas:**
       - Genera columnas con valores rezagados (`t-1`) y adelantados (`t+1`, `t+2`, `t+3`) de 'usd_clp'.

    5. **Transformación para estacionariedad:**
       - Calcula la primera diferencia logarítmica de 'usd_clp' para convertir la serie a estacionaria, creando las columnas 'y_t+0', 'y_t-1' y 'y_t-2'.

    6. **Pronósticos a 3 pasos adelante:**
       - Calcula diferencias logarítmicas para pronósticos a 1, 2 y 3 pasos adelante, generando las columnas 'y_t+1', 'y_t+2' y 'y_t+3'.

    7. **Integración de precios del cobre:**
       - Obtiene datos de precios del cobre utilizando la función `get_yfinance_data` con el ticker 'HG=F' (futuro del cobre a 3 meses) y un intervalo de fechas específico.
       - Fusiona estos datos con el DataFrame principal basado en la columna 'dates'.
        - TODO: cambiar ticker o validar data de tipos de cambio para evitar valores nulos al cruzar los datos.

    8. **Imputación de valores faltantes:**
       - Rellena los valores nulos en 'copper_close' utilizando el promedio de los valores de t-1 y t+1 para mantener la consistencia de la serie.
        - TODO: cambiar ticker o validar data de tipos de cambio para evitar valores nulos al cruzar los datos.

    9. **Transformación de precios del cobre:**
       - Calcula la primera diferencia logarítmica de 'copper_close' para convertir la serie a estacionaria, creando las columnas 'copper_t+0', 'copper_t-1', 'copper_t-2' y 'copper_t-3'.

    10. **Limpieza final:**
        - Elimina filas que contienen valores nulos en las columnas 'usd_clp' y 'copper_t-3' para asegurar la integridad de los datos preprocesados.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada que debe contener al menos las columnas 'dates' e 'iata'.

    market_calendar : object
        Objeto que representa el calendario de mercado cambiario utilizado para determinar los días hábiles.
        Debe ser compatible con la función `is_business_day`.

    Retorna
    -------
    pd.DataFrame
        DataFrame preprocesado que incluye variables rezagadas, adelantadas, diferencias logarítmicas
        y datos integrados de precios del cobre, listo para su uso en modelos de series de tiempo.

    Notas
    -----
    - La función `is_business_day` se utiliza para identificar días hábiles según el calendario proporcionado.
    - La función `get_yfinance_data` debe estar definida previamente y ser capaz de obtener datos de Yahoo Finance.
    - Las diferencias logarítmicas se calculan para transformar las series en estacionarias, lo cual es una
      suposición común en el análisis de series de tiempo.
    - Es importante que el DataFrame de entrada esté correctamente formateado y contenga las columnas necesarias
      para evitar errores durante el preprocesamiento.
    - La eliminación de filas con valores nulos en 'usd_clp' y 'copper_t-3' es crucial para garantizar que
      los datos estén completos y sean consistentes para el modelado posterior.

    Ejemplo
    -------
    ```python
    import pandas as pd

    # Supongamos que 'df' es un DataFrame con las columnas 'dates' e 'iata'
    # y 'market_calendar' es un objeto calendario adecuado.
    df_preprocesado = preprocessor(df, market_calendar)
    ```
    """

    df["dates"] = pd.to_datetime(df["dates"])
    df = df.sort_values(by="dates", ascending=True).reset_index(drop=True)
    df.rename(columns={"iata": "usd_clp"}, inplace=True)

    # Mantener los días no hábiles en la base propagando el último valor válido introducirá error en cálculo de estimadores.
    # Se utiliza calendario de mercado cambiario para determinar los dias hábiles.
    df["dummy_bd"] = df["dates"].apply(
        lambda x: is_business_day(x, market_calendar)
    )
    df = df.query("dummy_bd == 1").reset_index(drop=True)
    df.drop("dummy_bd", axis=1, inplace=True)

    df["usd_clp_t-1"] = df["usd_clp"].shift(1)
    df["usd_clp_t+1"] = df["usd_clp"].shift(-1)
    df["usd_clp_t+2"] = df["usd_clp"].shift(-2)
    df["usd_clp_t+3"] = df["usd_clp"].shift(-3)

    # Se calcula primera diferencia para convertir la serie a estacionaria
    df["y_t+0"] = np.log(df["usd_clp_t-1"]) - np.log(df["usd_clp"])
    df["y_t-1"] = df["y_t+0"].shift(1)
    df["y_t-2"] = df["y_t+0"].shift(2)

    # 3 Step Ahead
    df["y_t+1"] = np.log(df["usd_clp_t+1"]) - np.log(df["usd_clp"])
    df["y_t+2"] = np.log(df["usd_clp_t+2"]) - np.log(df["usd_clp"])
    df["y_t+3"] = np.log(df["usd_clp_t+3"]) - np.log(df["usd_clp"])

    # Precio del Cobre
    df_copper = get_yfinance_data(
        ticker_symbol="HG=F",
        date_interval=["2016-12-30", "2024-11-01"],
        name="copper"
    )

    df = df.merge(df_copper, how="left", on="dates")

    # Imputar nulos precio cobre con promedio entr t-1 y t+1
    df['copper_close'] = df['copper_close'].fillna(
        (df['copper_close'].shift(1) + df['copper_close'].shift(-1)) / 2)

    # Se calcula primera diferencia para convertir la serie a estacionaria
    df["copper_t+0"] = np.log(df["copper_close"]) - \
        np.log(df["copper_close"].shift())
    df["copper_t-1"] = df["copper_t+0"].shift(1)
    df["copper_t-2"] = df["copper_t+0"].shift(2)
    df["copper_t-3"] = df["copper_t+0"].shift(3)

    df.dropna(subset=["usd_clp", "copper_t-3"], inplace=True)

    return df


def train_inference_split(
        df: pd.DataFrame, last_train_date: str, market_calendar: list
) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    """
    Divide un DataFrame de series de tiempo en conjuntos de entrenamiento e inferencia, y genera fechas futuras para predicciones.

    El proceso de división incluye las siguientes etapas:

    1. **Ordenamiento y conversión de fechas:**
       - Ordena el DataFrame por la columna 'dates' de manera ascendente.
       - Convierte la columna 'dates' al tipo de dato datetime.

    2. **Procesamiento del calendario de mercado:**
       - Convierte y ordena las fechas proporcionadas en `market_calendar` al tipo datetime.

    3. **Validación y ajuste de la fecha de corte:**
       - Convierte `last_train_date` al tipo datetime.
       - Si `last_train_date` no está presente en las fechas del DataFrame, selecciona la fecha más cercana anterior. Si no existe ninguna fecha anterior, lanza un error.

    4. **División del DataFrame:**
       - **Conjunto de Entrenamiento (`df_train`):** Incluye todas las filas con fechas menores o iguales a `last_train_date`.
       - **Conjunto de Inferencia (`df_inference`):** Incluye las filas con fecha exactamente igual a `last_train_date`.

    5. **Generación de fechas futuras para predicciones:**
       - Combina las fechas del DataFrame con las del calendario de mercado y las ordena.
       - Identifica las siguientes tres fechas después de `last_train_date` para utilizarlas en predicciones a futuro.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada que debe contener al menos la columna 'dates'. Este DataFrame representa una serie de tiempo ordenada cronológicamente.

    last_train_date : str
        Fecha límite para el conjunto de entrenamiento en formato 'YYYY-MM-DD'. Si esta fecha no está presente en el DataFrame, se seleccionará la fecha más cercana anterior disponible.

    market_calendar : list
        Lista de fechas que representan el calendario de mercado cambiario. Estas fechas se utilizarán para determinar días hábiles y generar fechas futuras para predicciones.

    Retorna
    -------
    tuple[pd.DataFrame, pd.DataFrame, list]
        - **df_train (pd.DataFrame):** Subconjunto del DataFrame original que contiene todas las filas con fechas menores o iguales a `last_train_date`.
        - **df_inference (pd.DataFrame):** Subconjunto del DataFrame original que contiene las filas con fecha exactamente igual a `last_train_date`.
        - **next_dates (list):** Lista de tres cadenas de caracteres que representan las próximas fechas después de `last_train_date` en formato 'YYYY-MM-DD', basadas en el calendario de mercado.

    Raises
    ------
    ValueError
        - Si no se encuentra ninguna fecha anterior a `last_train_date` en el DataFrame.

    Notas
    -----
    - La función asume que la columna 'dates' en el DataFrame está correctamente formateada y contiene valores de fecha válidos.
    - Las fechas en `market_calendar` deben estar en un formato que pueda ser interpretado por `pd.to_datetime`.
    - La selección de las próximas fechas para predicciones se basa en la unión de las fechas del DataFrame y el calendario de mercado, asegurando que solo se consideren días hábiles definidos en el calendario.
    - Es importante que `market_calendar` incluya al menos tres fechas posteriores a `last_train_date` para evitar errores al generar `next_dates`.
    """

    df = df.sort_values(by="dates").reset_index(drop=True)
    df["dates"] = pd.to_datetime(df["dates"])

    calendar = sorted(pd.to_datetime(market_calendar))

    last_train_date = pd.to_datetime(last_train_date)
    if last_train_date not in df["dates"].values:
        closest_date = df.loc[df["dates"] < last_train_date, "dates"].max()
        if pd.isna(closest_date):
            raise ValueError("No hay ninguna fecha anterior en el DataFrame.")
        last_train_date = closest_date

    df_train = df.loc[df["dates"] <= last_train_date, :].reset_index(drop=True)
    df_inference = df.loc[df["dates"] ==
                          last_train_date, :].reset_index(drop=True)

    all_dates = sorted(set(df["dates"]).union(set(calendar)))

    current_index = all_dates.index(last_train_date)

    next_dates_dt = all_dates[current_index + 1: current_index + 4]
    next_dates = [date.strftime('%Y-%m-%d') for date in next_dates_dt]

    return df_train, df_inference, next_dates
