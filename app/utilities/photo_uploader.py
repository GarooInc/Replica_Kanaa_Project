import os
import requests
import random
import string
import logging
from datetime import datetime

# ==============================================================
# 🧠 CONFIGURACIÓN DE LOGGING
# ==============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ==============================================================
# 🔼 FUNCIÓN DE SUBIDA
# ==============================================================
def upload_to_server(file_tuple) -> str:
    """Sube un archivo al file server de Garoo y devuelve la URL pública."""
    resp = requests.post(
        "https://agents.garooinc.com/upload/itzana-agents",
        files={"file": file_tuple},
        headers={"User-Agent": "Mozilla/5.0"}
    )
    resp.raise_for_status()
    result = resp.json()

    if "url" not in result:
        raise ValueError("Respuesta inesperada del servidor: no se encontró la URL")

    return result["url"]

# ==============================================================
# 📸 FUNCIÓN PRINCIPAL
# ==============================================================
def upload_first_photo_found() -> str:
    """
    Busca la primera imagen en el proyecto (excluyendo ciertas carpetas),
    la sube al file server y la elimina del disco.
    Devuelve la URL como string.
    """
    base_dir = "."
    supported_ext = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
    excluded_dirs = {"data", ".idea", ".venv", "__pycache__", ".git", ".vscode", "node_modules"}

    logger.info("Buscando imágenes en el proyecto...")

    for root, dirs, files in os.walk(base_dir):
        # Excluir directorios definidos
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file.lower().endswith(supported_ext):
                file_path = os.path.join(root, file)
                try:
                    # Generar nombre aleatorio
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    rand_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=4))
                    new_filename = f"{timestamp}-{rand_suffix}.png"

                    logger.info(f"Subiendo archivo: {file_path}")
                    with open(file_path, "rb") as f:
                        file_tuple = (new_filename, f, "image/png")
                        url = upload_to_server(file_tuple)

                    os.remove(file_path)
                    logger.info(f"Subida exitosa y archivo eliminado: {file_path}")
                    logger.info(f"URL pública: {url}")
                    return url

                except Exception as e:
                    logger.warning(f"Error procesando {file_path}: {e}")
                    continue

    logger.warning("No se encontró ninguna imagen en el proyecto.")
    return None

# ==============================================================
# 🚀 EJECUCIÓN DIRECTA
# ==============================================================
if __name__ == "__main__":
    final_url = upload_first_photo_found()
    if final_url:
        print(final_url)
