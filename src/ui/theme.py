"""
Módulo de tokens visuales y tema para RedLocalBlock.
Basado en Branding.md y validado con WCAG 2.1 AA/AAA.
"""

from typing import Dict, Any

# ==========================================
# COLORES SEMÁNTICOS (Soporte Híbrido Claro / Oscuro)
# Formato Tupla (Modo Claro, Modo Oscuro) para CustomTkinter
# ==========================================
COLORS = {
    # Fondos y superficies
    "bg": ("#f8fafc", "#0f141c"),
    "surface": ("#ffffff", "#18202c"),
    "surface_hover": ("#f1f5f9", "#222c3d"),
    "border": ("#cbd5e1", "#293548"),
    "border_input": ("#94a3b8", "#64748b"),
    
    # Textos
    "text": ("#0f172a", "#f1f5f9"),
    "text_muted": ("#475569", "#94a3b8"),
    
    # Acciones y acentos
    "accent": ("#2563eb", "#2563eb"),
    "accent_hover": ("#1d4ed8", "#1d4ed8"),
    "on_accent": ("#ffffff", "#ffffff"),
    
    # Estados
    "danger": ("#dc2626", "#dc2626"),
    "danger_hover": ("#b91c1c", "#b91c1c"),
    "on_danger": ("#ffffff", "#ffffff"),
    
    "success": ("#047857", "#047857"),
    "success_hover": ("#065f46", "#065f46"),
    "on_success": ("#ffffff", "#ffffff"),
    
    "warning": ("#b45309", "#b45309"),
    "warning_hover": ("#92400e", "#92400e"),
    "on_warning": ("#ffffff", "#ffffff"),
    
    # Consola
    "console_bg": ("#f1f5f9", "#0b0e14"),
    "log_info": ("#2563eb", "#60a5fa"),
    "log_alert": ("#dc2626", "#f87171"),
    "log_success": ("#047857", "#34d399"),
    "log_warn": ("#b45309", "#fbbf24"),
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
