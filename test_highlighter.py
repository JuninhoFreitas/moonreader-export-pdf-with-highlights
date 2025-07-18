#!/usr/bin/env python3
"""
Script de teste para o Moon Highlighter
"""

import sqlite3
from pathlib import Path

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = sqlite3.connect("pdfmarks.sqlite")
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if cursor.fetchone():
            print("✓ Tabela 'notes' encontrada")
        else:
            print("✗ Tabela 'notes' não encontrada")
            return False
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM notes WHERE book = 'CONTEXTUALIZAÇÃO Missionária.pdf' AND bookmark = ''")
        count = cursor.fetchone()[0]
        print(f"✓ Encontrados {count} highlights para o livro")
        
        # Buscar alguns exemplos
        cursor.execute("""
            SELECT highlightColor, highlightLength, original 
            FROM notes 
            WHERE book = 'CONTEXTUALIZAÇÃO Missionária.pdf' AND bookmark = ''
            LIMIT 5
        """)
        
        examples = cursor.fetchall()
        print("\nExemplos de highlights:")
        for i, (color, length, text) in enumerate(examples, 1):
            print(f"  {i}. Cor: {color}, Comprimento: {length}")
            print(f"     Texto: {text[:100]}...")
            print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao conectar com banco: {e}")
        return False

def test_pdf_access():
    """Testa o acesso ao PDF"""
    pdf_path = Path("CONTEXTUALIZAÇÃO Missionária.pdf")
    
    if pdf_path.exists():
        print(f"✓ PDF encontrado: {pdf_path}")
        print(f"  Tamanho: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print(f"✗ PDF não encontrado: {pdf_path}")
        return False

def main():
    """Função principal do teste"""
    print("=== TESTE DO MOON HIGHLIGHTER ===\n")
    
    # Testar banco de dados
    print("1. Testando conexão com banco de dados...")
    db_ok = test_database_connection()
    
    print("\n2. Testando acesso ao PDF...")
    pdf_ok = test_pdf_access()
    
    print("\n=== RESULTADO ===")
    if db_ok and pdf_ok:
        print("✓ Todos os testes passaram!")
        print("A aplicação deve funcionar corretamente.")
    else:
        print("✗ Alguns testes falharam.")
        print("Verifique os problemas acima antes de executar a aplicação.")

if __name__ == "__main__":
    main() 