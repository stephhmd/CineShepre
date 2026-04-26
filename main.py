"""
Punto de entrada desde la raíz del proyecto.
"""
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    import uvicorn

    load_dotenv()

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )