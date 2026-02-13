"""
Exemplo: Como usar ícones Feather no EasyCut
"""
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from icon_manager import icon_manager, get_ui_icon

def demo_icons():
    """Demonstração dos ícones disponíveis"""
    root = tk.Tk()
    root.title("EasyCut - Demo Ícones")
    root.geometry("600x400")
    root.configure(bg="#0F1115")
    
    # Frame principal
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill='both', expand=True)
    
    # Título
    title = ttk.Label(
        frame,
        text="🎨 Ícones Feather Disponíveis",
        font=("Segoe UI", 14, "bold")
    )
    title.pack(pady=(0, 20))
    
    # Frame para botões
    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill='both', expand=True)
    
    # Lista de ícones para demonstrar
    demo_icons = [
        ("download", "Download"),
        ("verify", "Verificar"),
        ("music", "Áudio"),
        ("video", "Vídeo"),
        ("live", "Live"),
        ("record", "Gravar"),
        ("stop", "Parar"),
        ("folder", "Pasta"),
        ("refresh", "Atualizar"),
        ("trash-2", "Limpar"),
        ("github", "GitHub"),
        ("coffee", "Apoiar"),
        ("theme_dark", "Tema escuro"),
        ("theme_light", "Tema claro"),
        ("success", "Sucesso"),
        ("warning", "Aviso"),
    ]
    
    # Criar botões com ícones
    row = 0
    col = 0
    
    for icon_key, label in demo_icons:
        # Tentar pegar ícone
        icon = get_ui_icon(icon_key, size=20)
        
        # Criar botão
        btn = ttk.Button(
            buttons_frame,
            text=f"  {label}",
            image=icon if icon else None,
            compound="left",
            width=15
        )
        
        # Manter referência ao ícone
        if icon:
            btn.image = icon
        
        # Posicionar
        btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        col += 1
        if col > 3:
            col = 0
            row += 1
    
    # Info
    info = ttk.Label(
        frame,
        text="💡 Ícones usando emojis como fallback\n"
             "Para melhor qualidade, execute: python scripts/convert_icons.py",
        font=("Segoe UI", 9),
        foreground="#999"
    )
    info.pack(pady=(20, 0))
    
    # Listar ícones disponíveis
    available = icon_manager.list_icons()
    count_label = ttk.Label(
        frame,
        text=f"📦 {len(available)} ícones Feather SVG disponíveis",
        font=("Segoe UI", 9, "bold")
    )
    count_label.pack(pady=(10, 0))
    
    root.mainloop()


def demo_simple_button():
    """Exemplo simples de botão com ícone"""
    root = tk.Tk()
    root.title("Botão com Ícone")
    root.geometry("300x200")
    
    # Pegar ícone
    icon = get_ui_icon("download", size=16)
    
    # Criar botão
    btn = ttk.Button(
        root,
        text=" Download Vídeo",
        image=icon if icon else None,
        compound="left",
        command=lambda: print("Download iniciado!")
    )
    
    # IMPORTANTE: manter referência!
    if icon:
        btn.image = icon
    
    btn.pack(pady=50)
    
    # Info
    info = tk.Label(
        root,
        text="Clique no botão para testar",
        font=("Segoe UI", 9),
        fg="#666"
    )
    info.pack()
    
    root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("EasyCut - Demonstração de Ícones")
    print("=" * 50)
    print()
    print("1. Demo completa (todos os ícones)")
    print("2. Demo simples (um botão apenas)")
    print()
    
    choice = input("Escolha (1/2): ").strip()
    
    if choice == "2":
        demo_simple_button()
    else:
        demo_icons()
