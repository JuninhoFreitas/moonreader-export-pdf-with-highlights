#!/usr/bin/env python3
"""
Moon Highlighter - Versão Simplificada para Teste
"""

import argparse
import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional
from PyPDF2 import PdfReader, PdfWriter


class MoonHighlighterSimple:
    """Versão simplificada do MoonHighlighter para teste"""
    
    def __init__(self, pdf_path: str, book_name: str, db_path: str):
        self.pdf_path = Path(pdf_path)
        self.book_name = book_name
        self.db_path = Path(db_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {self.pdf_path}")
        if not self.db_path.exists():
            raise FileNotFoundError(f"Banco SQLite não encontrado: {self.db_path}")
    
    def get_sample_highlights(self, limit: int = 10) -> List[Tuple[str, int, str]]:
        """Busca uma amostra de highlights do banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT highlightColor, highlightLength, original 
            FROM notes 
            WHERE book = ? AND bookmark = ''
            LIMIT ?
            """
            
            cursor.execute(query, (self.book_name, limit))
            highlights = cursor.fetchall()
            
            conn.close()
            return highlights
            
        except sqlite3.Error as e:
            print(f"Erro ao acessar banco SQLite: {e}")
            return []
    
    def map_color(self, color_value: int) -> str:
        """Mapeia valor de cor do banco para cor hexadecimal"""
        color_map = {
            1996532479: "#FFFF00",    # Amarelo
            -1996554240: "#00FF00",   # Verde
            2013265664: "#0000FF",    # Azul
            -256: "#FF0000",          # Vermelho
            16711680: "#FF00FF",      # Rosa
        }
        
        if color_value in color_map:
            return color_map[color_value]
        
        # Cor padrão baseada no valor
        r = abs(color_value % 256)
        g = abs((color_value >> 8) % 256)
        b = abs((color_value >> 16) % 256)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def find_text_in_pdf(self, reader: PdfReader, text: str) -> List[Tuple[int, int, int]]:
        """Busca texto no PDF e retorna coordenadas aproximadas"""
        locations = []
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            
            if text in page_text:
                start_pos = page_text.find(text)
                lines_before = page_text[:start_pos].count('\n')
                x = 50
                y = 800 - (lines_before * 12)
                locations.append((page_num, x, y))
        
        return locations
    
    def process_sample_highlights(self, output_path: Optional[str] = None, limit: int = 10) -> str:
        """Processa uma amostra de highlights"""
        print(f"Processando {limit} highlights de teste para o livro: {self.book_name}")
        
        # Buscar amostra de highlights
        highlights = self.get_sample_highlights(limit)
        print(f"Encontrados {len(highlights)} highlights para teste")
        
        if not highlights:
            print("Nenhum highlight encontrado para processar")
            return ""
        
        # Abrir PDF
        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()
            
            # Copiar todas as páginas
            for page in reader.pages:
                writer.add_page(page)
                
        except Exception as e:
            print(f"Erro ao abrir PDF: {e}")
            return ""
        
        # Contadores
        total_highlights = len(highlights)
        found_highlights = 0
        not_found_highlights = 0
        
        # Processar cada highlight
        for i, (color_value, length, original_text) in enumerate(highlights):
            print(f"Processando highlight {i+1}/{total_highlights}: {original_text[:50]}...")
            
            color = self.map_color(color_value)
            locations = self.find_text_in_pdf(reader, original_text)
            
            if locations:
                found_highlights += 1
                print(f"  ✓ Encontrado ({len(locations)} ocorrências) - Cor: {color}")
            else:
                not_found_highlights += 1
                print(f"  ✗ Não encontrado no PDF")
        
        # Gerar caminho de saída
        if output_path is None:
            output_path = self.pdf_path.parent / f"{self.pdf_path.stem}_test_highlighted{self.pdf_path.suffix}"
        else:
            output_path = Path(output_path)
        
        # Salvar PDF
        try:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print(f"\nPDF de teste salvo: {output_path}")
        except Exception as e:
            print(f"Erro ao salvar PDF: {e}")
            return ""
        
        # Relatório
        print(f"\n=== RELATÓRIO DE TESTE ===")
        print(f"Total processado: {total_highlights}")
        print(f"Encontrados: {found_highlights}")
        print(f"Não encontrados: {not_found_highlights}")
        print(f"Taxa de sucesso: {(found_highlights/total_highlights)*100:.1f}%")
        
        return str(output_path)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Moon Highlighter - Versão de Teste",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python moon_highlighter_simple.py -p livro.pdf -b "livro.pdf" -d pdfmarks.sqlite
  python moon_highlighter_simple.py -p livro.pdf -b "livro.pdf" -d pdfmarks.sqlite -l 5
        """
    )
    
    parser.add_argument(
        "-p", "--pdf", 
        required=True,
        help="Caminho para o arquivo PDF"
    )
    
    parser.add_argument(
        "-b", "--book", 
        required=True,
        help="Nome do livro no banco de dados"
    )
    
    parser.add_argument(
        "-d", "--database", 
        required=True,
        help="Caminho para o banco SQLite"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Caminho de saída para o PDF com highlights (opcional)"
    )
    
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Número de highlights para processar (padrão: 10)"
    )
    
    args = parser.parse_args()
    
    try:
        highlighter = MoonHighlighterSimple(args.pdf, args.book, args.database)
        output_file = highlighter.process_sample_highlights(args.output, args.limit)
        
        if output_file:
            print(f"\nTeste concluído com sucesso!")
            print(f"Arquivo de saída: {output_file}")
            sys.exit(0)
        else:
            print("\nErro durante o teste")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 