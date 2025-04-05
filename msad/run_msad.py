#!/usr/bin/env python3
"""
MSAD - Punto de entrada principal
Ejecuta este script cuando quieras activar MSAD
"""
from msad.server import MSADServer

if __name__ == "__main__":
    print("Iniciando MSAD...")
    server = MSADServer()
    server.run_interactive() 