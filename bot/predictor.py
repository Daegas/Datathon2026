from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None


BOT_GREETING = "Hola soy pseudo-havi tu asistente de personalizacion. Analizando tu perfil y conversaciones..."


def _resolve_base_path() -> Path:
    env_path = os.getenv("PPATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _read_clusters(path: Path, stem: str, col_name: str) -> pd.DataFrame:
    parquet_path = path / "data" / "data_out" / f"{stem}.parquet"
    csv_path = path / "data" / "data_out" / f"{stem}.csv"

    if parquet_path.exists():
        clusters = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        clusters = pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(f"No se encontro {parquet_path.name} ni {csv_path.name}")

    if col_name not in clusters.columns:
        if "cluster" in clusters.columns:
            clusters = clusters.rename(columns={"cluster": col_name})
        elif "conv_cluster" in clusters.columns:
            clusters = clusters.rename(columns={"conv_cluster": col_name})

    if col_name not in clusters.columns:
        raise KeyError(
            f"No se encontro columna de cluster en {stem}. Columnas: {list(clusters.columns)}"
        )

    if "user_id" not in clusters.columns:
        raise KeyError(f"No se encontro user_id en {stem}")

    clusters = clusters[["user_id", col_name]].copy()
    clusters[col_name] = pd.to_numeric(clusters[col_name], errors="coerce")

    # Los exports del notebook pueden traer varias filas por usuario (una por conversacion).
    # Se consolida a 1 cluster por usuario usando la moda.
    clusters = (
        clusters.dropna(subset=[col_name])
        .groupby("user_id", as_index=False)[col_name]
        .agg(lambda s: int(s.mode().iloc[0]) if not s.mode().empty else int(s.iloc[0]))
    )
    return clusters


def _normalizar_user_id(msg: str) -> str | None:
    texto = msg.upper().strip()
    match = re.search(r"USR-\d{5}", texto)
    if match:
        return match.group(0)

    digits = re.sub(r"\D", "", texto)
    if not digits:
        return None

    return f"USR-{digits.zfill(5)[:5]}"


class PersonalizationBot:
    def __init__(self) -> None:
        self.base_path = _resolve_base_path()
        self.df: pd.DataFrame | None = None
        self.b2: pd.DataFrame | None = None
        self.model = None
        self.features: list[str] = []
        self.top_features: pd.Series | None = None
        self.fallback_cluster_input = 0
        self.fallback_cluster_output = 0

        self._cluster_input_desc = {
            0: "usuario que pregunta sobre saldos y movimientos",
            1: "usuario que pregunta sobre productos y beneficios",
            2: "usuario que reporta problemas o quejas",
        }
        self._cluster_output_desc = {
            0: "respuestas cortas y directas",
            1: "respuestas explicativas con contexto",
            2: "respuestas con opciones y alternativas",
        }

        self._score_buro_bueno = 650
        self._ingreso_alto = 25_000
        self._utilizacion_alta = 0.75
        self._saldo_inversion = 5_000
        self._satisfaccion_baja = 6.0

    def _predict_clusters_from_conversations(self, text_col: str, out_col: str) -> pd.DataFrame:
        conv_path = self.base_path / "data" / "dataset_conversaciones" / "dataset_50k_anonymized.parquet"
        if not conv_path.exists():
            return pd.DataFrame(columns=["user_id", out_col])

        conv = pd.read_parquet(conv_path)
        required = {"conv_id", "user_id", text_col}
        if not required.issubset(conv.columns):
            return pd.DataFrame(columns=["user_id", out_col])

        conv_agg = (
            conv.groupby("conv_id", as_index=False)
            .agg(
                user_id=("user_id", "first"),
                conv_text=(text_col, lambda x: " ".join(x.dropna().astype(str))),
            )
        )
        conv_agg["conv_text"] = conv_agg["conv_text"].fillna("").astype(str).str.strip()
        conv_agg = conv_agg[conv_agg["conv_text"].str.len() > 0].copy()
        if conv_agg.empty:
            return pd.DataFrame(columns=["user_id", out_col])

        vectorizer = TfidfVectorizer(max_features=4000, ngram_range=(1, 2), min_df=2)
        X = vectorizer.fit_transform(conv_agg["conv_text"]) 
        if X.shape[0] < 3:
            return pd.DataFrame(columns=["user_id", out_col])

        km = KMeans(n_clusters=3, random_state=42, n_init="auto")
        labels = km.fit_predict(X)

        pred = conv_agg[["user_id"]].copy()
        pred[out_col] = labels
        pred = (
            pred.groupby("user_id", as_index=False)[out_col]
            .agg(lambda s: int(s.mode().iloc[0]) if not s.mode().empty else int(s.iloc[0]))
        )
        return pred

    def _prepare(self) -> None:
        if self.model is not None and self.df is not None:
            return

        b1 = pd.read_csv(self.base_path / "data" / "hey_clientes.csv")
        b2 = pd.read_csv(self.base_path / "data" / "hey_productos.csv")
        b3 = pd.read_csv(self.base_path / "data" / "hey_transacciones.csv")
        self.b2 = b2.copy()

        b2_pivot = (
            b2.pivot_table(
                index="user_id",
                columns="tipo_producto",
                values="saldo_actual",
                aggfunc="sum",
                fill_value=0,
            )
            .reset_index()
        )

        b2_extra = (
            b2.groupby("user_id")
            .agg(
                num_productos=("producto_id", "count"),
                utilizacion_media=("utilizacion_pct", "mean"),
                saldo_total=("saldo_actual", "sum"),
            )
            .reset_index()
        )

        b3_agg = (
            b3.groupby("user_id")
            .agg(
                total_transacciones=("transaccion_id", "count"),
                monto_total=("monto", "sum"),
                cashback_total=("cashback_generado", "sum"),
                pct_internacional=("es_internacional", "mean"),
                pct_atipico=("patron_uso_atipico", "mean"),
            )
            .reset_index()
        )

        df = (
            b1.merge(b2_pivot, on="user_id", how="left")
            .merge(b2_extra, on="user_id", how="left")
            .merge(b3_agg, on="user_id", how="left")
        )

        clusters_input_exp = _read_clusters(self.base_path, "dataset_clusters_in", "cluster_input")
        clusters_output_exp = _read_clusters(self.base_path, "dataset_clusters_output", "cluster_output")

        clusters_input_pred = self._predict_clusters_from_conversations("input", "cluster_input")
        clusters_output_pred = self._predict_clusters_from_conversations("output", "cluster_output")

        users = df[["user_id"]].copy()
        users = users.merge(
            clusters_input_exp.rename(columns={"cluster_input": "cluster_input_exp"}),
            on="user_id",
            how="left",
        ).merge(
            clusters_output_exp.rename(columns={"cluster_output": "cluster_output_exp"}),
            on="user_id",
            how="left",
        ).merge(
            clusters_input_pred.rename(columns={"cluster_input": "cluster_input_pred"}),
            on="user_id",
            how="left",
        ).merge(
            clusters_output_pred.rename(columns={"cluster_output": "cluster_output_pred"}),
            on="user_id",
            how="left",
        )

        in_vals = pd.concat(
            [users["cluster_input_exp"], users["cluster_input_pred"]], axis=0
        ).dropna()
        out_vals = pd.concat(
            [users["cluster_output_exp"], users["cluster_output_pred"]], axis=0
        ).dropna()

        self.fallback_cluster_input = int(in_vals.mode().iloc[0]) if not in_vals.empty else 0
        self.fallback_cluster_output = int(out_vals.mode().iloc[0]) if not out_vals.empty else 0

        users["conv_cluster_x"] = users["cluster_input_exp"].combine_first(users["cluster_input_pred"])
        users["conv_cluster_y"] = users["cluster_output_exp"].combine_first(users["cluster_output_pred"])

        users["cluster_input_source"] = np.where(
            users["cluster_input_exp"].notna(),
            "export_eda",
            np.where(users["cluster_input_pred"].notna(), "kmeans_repredict", "fallback"),
        )
        users["cluster_output_source"] = np.where(
            users["cluster_output_exp"].notna(),
            "export_eda",
            np.where(users["cluster_output_pred"].notna(), "kmeans_repredict", "fallback"),
        )

        users["conv_cluster_x"] = users["conv_cluster_x"].fillna(self.fallback_cluster_input).astype(int)
        users["conv_cluster_y"] = users["conv_cluster_y"].fillna(self.fallback_cluster_output).astype(int)

        df = df.merge(
            users[[
                "user_id",
                "conv_cluster_x",
                "conv_cluster_y",
                "cluster_input_source",
                "cluster_output_source",
            ]],
            on="user_id",
            how="left",
        ).fillna(0)

        bool_cols = df.select_dtypes(include="bool").columns
        if len(bool_cols) > 0:
            df[bool_cols] = df[bool_cols].astype(int)

        target = "satisfaccion_1_10"
        candidate_features = [
            "edad",
            "ingreso_mensual_mxn",
            "antiguedad_dias",
            "score_buro",
            "dias_desde_ultimo_login",
            "num_productos_activos",
            "es_hey_pro",
            "nomina_domiciliada",
            "recibe_remesas",
            "usa_hey_shop",
            "tiene_seguro",
            "patron_uso_atipico",
            "num_productos",
            "utilizacion_media",
            "saldo_total",
            "total_transacciones",
            "monto_total",
            "cashback_total",
            "pct_internacional",
            "pct_atipico",
            "conv_cluster_x",
            "conv_cluster_y",
        ]

        self.features = [c for c in candidate_features if c in df.columns]
        if not self.features:
            raise ValueError("No hay columnas de features disponibles para el modelo")

        X = df[self.features].replace([np.inf, -np.inf], np.nan).fillna(0)
        y = df[target]

        mask = y.notna() & np.isfinite(y)
        X = X[mask].reset_index(drop=True)
        y = y[mask].reset_index(drop=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        if XGBRegressor is None:
            raise ImportError(
                "xgboost no esta disponible en el entorno. Instala xgboost para usar el nuevo modelo."
            )

        model = XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            random_state=42,
        )
        model.fit(X_train, y_train)

        pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        print(f"Modelo entrenado (XGBoost). MAE: {mae:.3f}")

        importances = pd.Series(model.feature_importances_, index=self.features)
        self.top_features = importances.sort_values(ascending=False)
        self.df = df
        self.model = model

    def _obtener_productos_activos(self, user_id: str) -> list[str]:
        if self.b2 is None:
            return []
        prod = self.b2[self.b2["user_id"] == user_id]["tipo_producto"].dropna().astype(str)
        return prod.unique().tolist()

    def _recomendaciones_producto(self, user_id: str, row: pd.Series, sat_pred: float) -> list[str]:
        productos_actuales = self._obtener_productos_activos(user_id)
        recomendaciones: list[str] = []

        ingreso = float(row.get("ingreso_mensual_mxn", 0) or 0)
        score = float(row.get("score_buro", 0) or 0)
        utilizacion = float(row.get("utilizacion_media", 0) or 0)
        saldo_total = float(row.get("saldo_total", 0) or 0)
        cashback = float(row.get("cashback_total", 0) or 0)
        tiene_seguro = bool(row.get("tiene_seguro", 0))
        nomina = bool(row.get("nomina_domiciliada", 0))
        dias_login = float(row.get("dias_desde_ultimo_login", 0) or 0)

        if score >= self._score_buro_bueno and ingreso >= self._ingreso_alto:
            if "tarjeta_credito_hey" not in productos_actuales:
                recomendaciones.append(
                    "Tarjeta de credito Hey por perfil crediticio solido e ingresos estables."
                )
            if "tarjeta_credito_negocios" not in productos_actuales and ingreso >= 40_000:
                recomendaciones.append(
                    "Tarjeta de credito Negocios por nivel de ingresos alto."
                )

        if score >= self._score_buro_bueno and "credito_auto" not in productos_actuales:
            recomendaciones.append("Credito Auto con condiciones preferenciales por buen score.")

        if nomina and "credito_nomina" not in productos_actuales:
            recomendaciones.append("Credito Nomina por nomina domiciliada activa.")

        if score < self._score_buro_bueno and "tarjeta_credito_garantizada" not in productos_actuales:
            recomendaciones.append("Tarjeta de credito Garantizada para construir historial.")

        if utilizacion >= self._utilizacion_alta and score >= self._score_buro_bueno:
            recomendaciones.append("Aumento de limite de credito por alta utilizacion y buen score.")

        if "inversion_hey" not in productos_actuales and saldo_total >= self._saldo_inversion:
            recomendaciones.append("Inversion Hey para generar rendimiento sobre saldo disponible.")

        if "cuenta_negocios" not in productos_actuales and ingreso >= 30_000:
            recomendaciones.append("Cuenta Negocios por compatibilidad con perfil de ingresos.")

        if not tiene_seguro:
            if "seguro_vida" not in productos_actuales:
                recomendaciones.append("Seguro de Vida para cobertura base segun perfil.")
            if "seguro_compras" not in productos_actuales:
                recomendaciones.append("Seguro de Compras para proteger transacciones frecuentes.")

        if dias_login > 30:
            recomendaciones.append("Recordatorio de beneficios por inactividad reciente en la app.")

        if cashback == 0 and "tarjeta_credito_hey" in productos_actuales:
            recomendaciones.append("Activar estrategia de uso de tarjeta para generar cashback.")

        if sat_pred < self._satisfaccion_baja:
            recomendaciones.append("Priorizar seguimiento proactivo por satisfaccion estimada baja.")

        if not recomendaciones:
            recomendaciones.append("Usuario con portafolio estable; mantener acompanamiento y ofertas contextuales.")

        return recomendaciones

    def bot_personalizado(self, user_id: str) -> str:
        self._prepare()
        assert self.df is not None and self.model is not None

        row_df = self.df[self.df["user_id"] == user_id]
        if row_df.empty:
            return "Usuario no encontrado. Escribe un user_id valido como USR-00003."

        row = row_df.iloc[0]
        x_user = pd.DataFrame([row[self.features]]).fillna(0)
        sat_pred = float(self.model.predict(x_user)[0])

        cl_in = int(row.get("conv_cluster_x", self.fallback_cluster_input))
        cl_out = int(row.get("conv_cluster_y", self.fallback_cluster_output))

        perfil_conv = self._cluster_input_desc.get(cl_in, "perfil desconocido")
        estilo_resp = self._cluster_output_desc.get(cl_out, "estilo estandar")

        sugerencias = self._recomendaciones_producto(user_id, row, sat_pred)

        respuesta = [
            "Sugerencias para mejorar satisfaccion:",
        ]
        respuesta.extend([f"  {i}. {s}" for i, s in enumerate(sugerencias, start=1)])

        src_in = str(row.get("cluster_input_source", ""))
        src_out = str(row.get("cluster_output_source", ""))
        if src_in == "fallback" or src_out == "fallback":
            respuesta.extend(
                [
                    "",
                    "Nota: este usuario no tiene conversaciones suficientes; se uso cluster fallback poblacional.",
                    "Sugerencia: calcular cluster con un modelo auxiliar basado en perfil financiero para cubrir cold-start.",
                ]
            )

        return "\n".join(respuesta)


def mensaje_inicial() -> str:
    return BOT_GREETING


_BOT = PersonalizationBot()


def bot_personalizado(user_id: str) -> str:
    return _BOT.bot_personalizado(user_id)


def responder_mensaje(msg: str) -> str:
    user_id = _normalizar_user_id(msg)
    if not user_id:
        return "Envia solo los 5 digitos de tu user_id (ejemplo: 00003) para generar la prediccion personalizada."
    return bot_personalizado(user_id)
