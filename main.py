import argparse
import pandas as pd
import pprint

from src.preprocessor import preprocessor, train_inference_split
from src.model import TimeSeriesLinearRegression
from lib.calendar import get_market_calendar


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--last-train-date",
        default="2024-10-24",
    )
    parser.add_argument(
        "--confidence-level",
        type=float,
        default=.95,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Importar Datos
    df = pd.read_csv("./data/raw/exchangeRateIATA.csv", sep=";")

    # Se obtiene el Calendario de Mercado para excluir dias no hábiles.
    # Los días no habiles tienen retorno = 0.0 lo que introduce error en el cálculo de estimadores.
    market_calendar = get_market_calendar(
        market="CME_Currency", date_interval=["2016-12-28", "2024-11-01"]
    )

    # Procesamiento de datos
    #   - Cálculo de primeras diferencias y rezagos de la variable endógena.
    #   - Se añade variable exógina: Diferencias y Rezagos del precio del cobre.
    df = preprocessor(df, market_calendar)

    # Se separa la base en set de entrenamiento e inferencia
    df_train, df_inference, next_dates = train_inference_split(
        df, args.last_train_date, market_calendar=market_calendar
    )

    # Se genera un dataset de entrenamiento por cada horizonte de prediccion.
    df_train_t1 = df_train.dropna(subset=["y_t+1"]).reset_index(drop=True)
    df_train_t2 = df_train.dropna(subset=["y_t+2"]).reset_index(drop=True)
    df_train_t3 = df_train.dropna(subset=["y_t+3"]).reset_index(drop=True)

    # Se definen las variables independientes.
    # Ver notebooks para detalles de la especificacion y experimento.
    #   - y_t+0: retorno del tipo de cambio de hoy. En simple: diferencia porcental entre el precio de ayer y hoy.
    #   - y_t-1: retorno del tipo de cambio de ayer. En simple: diferencia porcental entre el precio de antes de ayer y ayer.
    #   - Misma definicion para los retornos del cobre.
    independent_variables = [
        "y_t+0", "y_t-1", "copper_t+0", "copper_t-1", "copper_t-2", "copper_t-3"
    ]

    # Se generan las matrices de caracteristicas por cada horizonte de predicción
    X_train_t1 = df_train_t1[independent_variables]
    X_train_t2 = df_train_t2[independent_variables]
    X_train_t3 = df_train_t3[independent_variables]

    # Se generan los vectores de la variable dependiente por cada horizonte de predicción.
    y_train_t1 = df_train_t1["y_t+1"]
    y_train_t2 = df_train_t2["y_t+2"]
    y_train_t3 = df_train_t3["y_t+3"]

    # Se genera la matriz de caracteísticas para la inferencia
    X_inference = df_inference[independent_variables]

    # Se define una instancia del Modelo de Regresión Personalizado por cada horizonte de prediccion.
    # La unica diferencia entre este modelo y un modelo de Regresión Lineal es que el modelo
    # personalizado almacena los errores fuera de muestra dentro del conjunto de entrenamient
    # para el posterior calculo de intervalo de confianza.
    model_t1 = TimeSeriesLinearRegression(
        confidence_level=args.confidence_level
    )
    model_t2 = TimeSeriesLinearRegression(
        confidence_level=args.confidence_level
    )
    model_t3 = TimeSeriesLinearRegression(
        confidence_level=args.confidence_level
    )

    # Se ajustan los modelos.
    model_t1.fit(X_train_t1, y_train_t1)
    model_t2.fit(X_train_t2, y_train_t2)
    model_t3.fit(X_train_t3, y_train_t3)

    # Se generan las predicciones por horizonte de predicción.
    y_pred_t1, lower_bound_t1, upper_bound_t1 = model_t1.predict(X_inference)
    y_pred_t2, lower_bound_t2, upper_bound_t2 = model_t2.predict(X_inference)
    y_pred_t3, lower_bound_t3, upper_bound_t3 = model_t3.predict(X_inference)

    # Identificación de datos para reporte final.
    y_t0 = float(df_inference["usd_clp"][0])

    y_actual_usd_t1 = float(df_inference["usd_clp_t+1"][0])
    y_actual_usd_t2 = float(df_inference["usd_clp_t+2"][0])
    y_actual_usd_t3 = float(df_inference["usd_clp_t+3"][0])

    y_actual_var_t1 = float(df_inference["y_t+1"][0])
    y_actual_var_t2 = float(df_inference["y_t+2"][0])
    y_actual_var_t3 = float(df_inference["y_t+3"][0])

    y_pred_usd_t1 = y_t0 * (1 + y_pred_t1)
    y_pred_usd_t2 = y_t0 * (1 + y_pred_t2)
    y_pred_usd_t3 = y_t0 * (1 + y_pred_t3)

    y_pred_usd_t1_ci = [y_t0 * (1 + lower_bound_t1),
                        y_t0 * (1 + upper_bound_t1)]
    y_pred_usd_t2_ci = [y_t0 * (1 + lower_bound_t2),
                        y_t0 * (1 + upper_bound_t2)]
    y_pred_usd_t3_ci = [y_t0 * (1 + lower_bound_t3),
                        y_t0 * (1 + upper_bound_t3)]

    y_date_t0 = df_inference["dates"][0].strftime('%Y-%m-%d')

    # Generacion de reporte final
    prediction = {
        "current_date": y_date_t0,
        "forecast": {
            "t+1": {
                "date_t+1": next_dates[0],
                "usd_t+0": y_t0,
                "usd_forecast": y_pred_usd_t1,
                "usd_forecast_confidence": {"confidence_level": args.confidence_level, "interval": y_pred_usd_t1_ci},
                "usd_observed": None if pd.isna(y_actual_usd_t1) else y_actual_usd_t1,
                "variation_forecast": y_pred_t1,
                "variation_observed": None if pd.isna(y_actual_var_t1) else y_actual_var_t1,
            },
            "t+2": {
                "date_t+2": next_dates[1],
                "usd_t+0": y_t0,
                "usd_forecast": y_pred_usd_t2,
                "usd_forecast_confidence": {"confidence_level": args.confidence_level, "interval": y_pred_usd_t2_ci},
                "usd_observed": None if pd.isna(y_actual_usd_t2) else y_actual_usd_t2,
                "variation_forecast": y_pred_t2,
                "variation_observed": None if pd.isna(y_actual_var_t2) else y_actual_var_t2,
            },
            "t+3": {
                "date_t+1": next_dates[2],
                "usd_t+0": y_t0,
                "usd_forecast": y_pred_usd_t3,
                "usd_forecast_confidence": {"confidence_level": args.confidence_level, "interval": y_pred_usd_t3_ci},
                "usd_observed": None if pd.isna(y_actual_usd_t3) else y_actual_usd_t3,
                "variation_forecast": y_pred_t3,
                "variation_observed": None if pd.isna(y_actual_var_t3) else y_actual_var_t3,
            },
        }
    }

    # Reporte final para el usuario.
    pprint.pp(prediction)
