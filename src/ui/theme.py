"""
Módulo de tokens visuales y tema para RedLocalBlock.
Basado en Branding.md y validado con WCAG 2.1 AA/AAA.
"""

from typing import Dict, Any

# ==========================================
# COLORES SEMÁNTICOS (Dark Mode Primario)
# ==========================================
COLORS = {
    # Fondos y superficies
    "bg": "#0f141c",
    "surface": "#18202c",
    "surface_hover": "#222c3d",
    "border": "#293548",
    "border_input": "#64748b",
    
    # Textos
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    
    # Acciones y acentos
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "on_accent": "#ffffff",
    
    # Estados
    "danger": "#dc2626",
    "danger_hover": "#b91c1c",
    "on_danger": "#ffffff",
    
    "success": "#047857",
    "success_hover": "#065f46",
    "on_success": "#ffffff",
    
    "warning": "#b45309",
    "warning_hover": "#92400e",
    "on_warning": "#ffffff",
    
    # Consola
    "console_bg": "#0b0e14",
    "log_info": "#60a5fa",
    "log_alert": "#f87171",
    "log_success": "#34d399",
    "log_warn": "#fbbf24",
}

# ==========================================
# TIPOGRAFÍA DEL SISTEMA (DSGVO Compliant)
# ==========================================
FONTS = {
    "family_sans": "Segoe UI",
    "family_mono": "Consolas",
    "sizes": {
        "xs": 11,
        "sm": 12,
        "base": 14,
        "md": 16,
        "lg": 20,
        "xl": 24,
    }
}

# ==========================================
# ESPACIADO Y RADIOS
# ==========================================
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}

RADII = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "pill": 999,
}
