from pydantic import BaseModel
from typing import Literal, Optional, List

class DatosPaciente(BaseModel):
    sexo: Literal["hombre", "mujer"]
    edad: int
    peso_kg: float
    estatura_cm: float
    nivel_actividad: Literal["sedentario", "ligero", "moderado", "alto", "atleta"]
    objetivo: Literal["perder_grasa","ganar_musculo","mantener","rendimiento","salud_metabolica"]
    porcentaje_grasa: Optional[float] = None
    preferencia_formula: Literal["mifflin", "harris", "directa"] = "mifflin"

class PlanNutricional(BaseModel):
    tmb: float
    tdee: float
    calorias_objetivo: float
    proteinas_g: float
    grasas_g: float
    carbohidratos_g: float
    recomendaciones: List[str]

# ---- Cálculos ---- #

def calcular_tmb_mifflin(sexo, peso, estatura, edad):
    return 10*peso + 6.25*estatura - 5*edad + (5 if sexo=="hombre" else -161)

def calcular_tmb_harris(sexo, peso, estatura, edad):
    if sexo=="hombre":
        return 66.5 + 13.75*peso + 5.003*estatura - 6.775*edad
    return 655.1 + 9.563*peso + 1.85*estatura - 4.676*edad

def factor_actividad(nivel):
    return {
        "sedentario": 1.2,
        "ligero": 1.375,
        "moderado": 1.55,
        "alto": 1.725,
        "atleta": 1.9
    }[nivel]

def generar_plan_nutricional(datos: DatosPaciente):
    if datos.preferencia_formula=="mifflin":
        tmb = calcular_tmb_mifflin(datos.sexo, datos.peso_kg, datos.estatura_cm, datos.edad)
    else:
        tmb = calcular_tmb_harris(datos.sexo, datos.peso_kg, datos.estatura_cm, datos.edad)

    tdee = tmb * factor_actividad(datos.nivel_actividad)

    if datos.objetivo=="perder_grasa":
        calorias = tdee * 0.80
    elif datos.objetivo=="ganar_musculo":
        calorias = tdee * 1.15
    else:
        calorias = tdee

    proteinas = datos.peso_kg * 1.8
    grasas = calorias * 0.25 / 9
    carbs = (calorias - (proteinas*4 + grasas*9)) / 4

    return PlanNutricional(
        tmb=round(tmb,1),
        tdee=round(tdee,1),
        calorias_objetivo=round(calorias,1),
        proteinas_g=round(proteinas,1),
        grasas_g=round(grasas,1),
        carbohidratos_g=round(carbs,1),
        recomendaciones=[
            "Distribuye carbohidratos alrededor del entrenamiento.",
            "Incluye proteína magra en cada comida.",
            "Usa electrolitos en sesiones largas."
        ]
    )
