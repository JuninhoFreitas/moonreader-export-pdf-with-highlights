#!/usr/bin/env python3
"""
Moon Highlighter - Aplicação Python para marcar highlights em PDFs baseado em dados SQLite

Esta aplicação:
1. Recebe caminho do PDF, nome do livro e caminho do banco SQLite
2. Executa query no banco para buscar highlights
3. Localiza o texto no PDF e cria marcações visuais reais
4. Salva um novo PDF com os highlights
5. Inclui busca fuzzy para melhor precisão
6. Interface gráfica opcional

Melhorias implementadas:
- PyMuPDF para highlights visuais reais
- Busca fuzzy de texto
- Coordenadas precisas usando quads
- Interface gráfica opcional
"""

import argparse
import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import fitz  # PyMuPDF
from fuzzywuzzy import fuzz, process
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading


class MoonHighlighter:
    """Classe principal para processar highlights em PDFs com melhorias avançadas"""
    
    def __init__(self, pdf_path: str, book_name: str, db_path: str):
        """
        Inicializa o MoonHighlighter
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            book_name: Nome do livro no banco de dados
            db_path: Caminho para o banco SQLite
        """
        self.pdf_path = Path(pdf_path)
        self.book_name = book_name
        self.db_path = Path(db_path)
        
        # Validar arquivos
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {self.pdf_path}")
        if not self.db_path.exists():
            raise FileNotFoundError(f"Banco SQLite não encontrado: {self.db_path}")
        
        # Configurações de busca fuzzy
        self.fuzzy_threshold = 80  # Limiar para busca fuzzy (0-100)
        self.max_fuzzy_results = 5  # Máximo de resultados fuzzy por texto
        
        # Cache para texto extraído
        self.text_cache = {}
        
    def get_highlights_from_db(self) -> List[Tuple[str, int, str]]:
        """
        Busca highlights do banco SQLite
        
        Returns:
            Lista de tuplas (highlightColor, highlightLength, original)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT highlightColor, highlightLength, original 
            FROM notes 
            WHERE book = ? AND bookmark = ''
            """
            
            cursor.execute(query, (self.book_name,))
            highlights = cursor.fetchall()
            
            conn.close()
            return highlights
            
        except sqlite3.Error as e:
            print(f"Erro ao acessar banco SQLite: {e}")
            return []
    
    def map_color(self, color_value: int) -> Tuple[float, float, float]:
        """
        Mapeia valor de cor do banco para cor RGB (0-1)
        
        Args:
            color_value: Valor da cor do banco
            
        Returns:
            Tupla RGB (r, g, b) com valores entre 0 e 1
        """
        # Mapeamento avançado baseado no valor da cor
        color_map = {
            1996532479: (1.0, 1.0, 0.0),    # Amarelo
            -1996554240: (0.0, 1.0, 0.0),   # Verde
            2013265664: (0.0, 0.0, 1.0),    # Azul
            -256: (1.0, 0.0, 0.0),          # Vermelho
            16711680: (1.0, 0.0, 1.0),      # Rosa/Magenta
        }
        
        # Se a cor está no mapa, use ela
        if color_value in color_map:
            return color_map[color_value]
        
        # Caso contrário, calcule uma cor baseada no valor
        r = abs(color_value % 256) / 255.0
        g = abs((color_value >> 8) % 256) / 255.0
        b = abs((color_value >> 16) % 256) / 255.0
        
        return (r, g, b)
    
    def extract_page_text(self, page: fitz.Page) -> str:
        """
        Extrai texto de uma página com cache
        
        Args:
            page: Página do PDF
            
        Returns:
            Texto extraído da página
        """
        page_num = page.number
        if page_num not in self.text_cache:
            self.text_cache[page_num] = page.get_text()
        return self.text_cache[page_num]
    
    def find_text_exact(self, page: fitz.Page, text: str) -> List[fitz.Quad]:
        """
        Busca texto exato no PDF usando PyMuPDF
        
        Args:
            page: Página do PDF
            text: Texto a ser buscado
            
        Returns:
            Lista de quads onde o texto foi encontrado
        """
        try:
            # Busca exata usando PyMuPDF
            quads = page.search_for(text, quads=True)
            return quads
        except Exception as e:
            print(f"Erro na busca exata: {e}")
            return []
    
    def find_text_fuzzy(self, page: fitz.Page, text: str) -> List[Tuple[fitz.Quad, float]]:
        """
        Busca texto usando busca fuzzy
        
        Args:
            page: Página do PDF
            text: Texto a ser buscado
            
        Returns:
            Lista de tuplas (quad, score) com os melhores matches
        """
        try:
            # Extrair todas as palavras da página
            page_text = self.extract_page_text(page)
            words = page.get_text("words")
            
            # Buscar palavras similares
            similar_words = []
            for word in words:
                word_text = word[4]  # O texto da palavra
                if len(word_text) > 3:  # Ignorar palavras muito curtas
                    score = fuzz.partial_ratio(text.lower(), word_text.lower())
                    if score >= self.fuzzy_threshold:
                        similar_words.append((word, score))
            
            # Ordenar por score e pegar os melhores
            similar_words.sort(key=lambda x: x[1], reverse=True)
            best_matches = similar_words[:self.max_fuzzy_results]
            
            # Converter para quads
            quads_with_scores = []
            for word, score in best_matches:
                # Criar quad a partir das coordenadas da palavra
                x0, y0, x1, y1 = word[:4]
                quad = fitz.Quad(fitz.Point(x0, y0), fitz.Point(x1, y0), 
                               fitz.Point(x1, y1), fitz.Point(x0, y1))
                quads_with_scores.append((quad, score))
            
            return quads_with_scores
            
        except Exception as e:
            print(f"Erro na busca fuzzy: {e}")
            return []
    
    def add_highlight_annotation(self, page: fitz.Page, quads: List[fitz.Quad], 
                               color: Tuple[float, float, float], text: str) -> bool:
        """
        Adiciona anotação de highlight real na página
        
        Args:
            page: Página do PDF
            quads: Lista de quads onde adicionar o highlight
            color: Cor RGB (r, g, b) entre 0 e 1
            text: Texto destacado
            
        Returns:
            True se o highlight foi adicionado com sucesso
        """
        try:
            if not quads:
                return False
            
            # Adicionar highlight usando PyMuPDF
            annot = page.add_highlight_annot(quads)
            
            # Configurar cor personalizada
            annot.set_colors(stroke=color)
            
            # Adicionar conteúdo à anotação
            annot.set_info(content=f"Highlight: {text[:100]}...")
            
            # Atualizar a anotação
            annot.update()
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar highlight: {e}")
            return False
    
    def process_highlights(self, output_path: Optional[str] = None, 
                          use_fuzzy: bool = True, 
                          progress_callback=None) -> str:
        """
        Processa todos os highlights e salva o PDF
        
        Args:
            output_path: Caminho de saída (opcional)
            use_fuzzy: Se deve usar busca fuzzy
            progress_callback: Função de callback para progresso
            
        Returns:
            Caminho do arquivo de saída
        """
        print(f"Processando highlights para o livro: {self.book_name}")
        
        # Buscar highlights do banco
        highlights = self.get_highlights_from_db()
        print(f"Encontrados {len(highlights)} highlights no banco de dados")
        
        if not highlights:
            print("Nenhum highlight encontrado para processar")
            return ""
        
        # Abrir PDF
        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            print(f"Erro ao abrir PDF: {e}")
            return ""
        
        # Contadores para relatório
        total_highlights = len(highlights)
        found_highlights = 0
        not_found_highlights = 0
        fuzzy_highlights = 0
        
        # Processar cada highlight
        for i, (color_value, length, original_text) in enumerate(highlights):
            if progress_callback:
                progress_callback(i, total_highlights, f"Processando: {original_text[:50]}...")
            
            print(f"Processando highlight {i+1}/{total_highlights}: {original_text[:50]}...")
            
            # Mapear cor
            color = self.map_color(color_value)
            
            # Buscar texto no PDF
            found_quads = []
            fuzzy_used = False
            
            # Tentar busca exata primeiro
            for page in doc:
                quads = self.find_text_exact(page, original_text)
                if quads:
                    found_quads.extend(quads)
                    break
            
            # Se não encontrou e fuzzy está habilitado, tentar busca fuzzy
            if not found_quads and use_fuzzy:
                for page in doc:
                    fuzzy_results = self.find_text_fuzzy(page, original_text)
                    if fuzzy_results:
                        # Pegar o melhor match
                        best_quad, score = fuzzy_results[0]
                        found_quads = [best_quad]
                        fuzzy_used = True
                        print(f"  🔍 Match fuzzy encontrado (score: {score}%)")
                        break
            
            if found_quads:
                # Adicionar highlights em todas as ocorrências encontradas
                for page in doc:
                    page_quads = [q for q in found_quads if q in page.search_for(original_text, quads=True)]
                    if page_quads:
                        success = self.add_highlight_annotation(page, page_quads, color, original_text)
                        if success:
                            found_highlights += 1
                            if fuzzy_used:
                                fuzzy_highlights += 1
                            print(f"  ✓ Highlight adicionado ({len(page_quads)} ocorrências)")
                        else:
                            not_found_highlights += 1
                            print(f"  ✗ Erro ao adicionar highlight")
                        break
                else:
                    not_found_highlights += 1
                    print(f"  ✗ Não encontrado no PDF")
            else:
                not_found_highlights += 1
                print(f"  ✗ Não encontrado no PDF")
        
        # Gerar caminho de saída
        if output_path is None:
            output_path = self.pdf_path.parent / f"{self.pdf_path.stem}_highlighted{self.pdf_path.suffix}"
        else:
            output_path = Path(output_path)
        
        # Salvar PDF com highlights
        try:
            doc.save(output_path)
            doc.close()
            print(f"\nPDF salvo com sucesso: {output_path}")
        except Exception as e:
            print(f"Erro ao salvar PDF: {e}")
            return ""
        
        # Relatório final
        print(f"\n=== RELATÓRIO FINAL ===")
        print(f"Total de highlights processados: {total_highlights}")
        print(f"Highlights encontrados e aplicados: {found_highlights}")
        print(f"Highlights usando busca fuzzy: {fuzzy_highlights}")
        print(f"Highlights não encontrados: {not_found_highlights}")
        
        if progress_callback:
            progress_callback(total_highlights, total_highlights, "Processamento concluído!")
        
        return str(output_path)


class MoonHighlighterGUI:
    """Interface gráfica para o Moon Highlighter"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Moon Highlighter - Processador de Highlights")
        self.root.geometry("800x600")
        
        self.highlighter = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Moon Highlighter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Campos de entrada
        ttk.Label(main_frame, text="Arquivo PDF(pdf path):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pdf_var = tk.StringVar()
        pdf_entry = ttk.Entry(main_frame, textvariable=self.pdf_var, width=50)
        pdf_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Procurar", 
                  command=self.browse_pdf).grid(row=1, column=2, pady=5)
        
        ttk.Label(main_frame, text="Nome do Livro(book name):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.book_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.book_var, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        ttk.Label(main_frame, text="Banco SQLite(sqlite path):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.db_var = tk.StringVar()
        db_entry = ttk.Entry(main_frame, textvariable=self.db_var, width=50)
        db_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Procurar", 
                  command=self.browse_db).grid(row=3, column=2, pady=5)
        
        ttk.Label(main_frame, text="Arquivo de Saída(output path):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Procurar", 
                  command=self.browse_output).grid(row=4, column=2, pady=5)
        
        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        self.fuzzy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Usar busca fuzzy(use fuzzy search)", 
                       variable=self.fuzzy_var).grid(row=0, column=0, sticky=tk.W)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Processar Highlights(process highlights)", 
                  command=self.process_highlights).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar(clear)", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sair(exit)", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Log(log)", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamento
        main_frame.rowconfigure(8, weight=1)
    
    def browse_pdf(self):
        """Abre diálogo para selecionar arquivo PDF"""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo PDF(select pdf file)",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_var.set(filename)
            # Auto-preencher nome do livro
            if not self.book_var.get():
                self.book_var.set(Path(filename).name)
    
    def browse_db(self):
        """Abre diálogo para selecionar banco SQLite"""
        filename = filedialog.askopenfilename(
            title="Selecionar banco SQLite(select sqlite file)",
            filetypes=[("SQLite files", "*.sqlite"), ("All files", "*.*")]
        )
        if filename:
            self.db_var.set(filename)
    
    def browse_output(self):
        """Abre diálogo para selecionar arquivo de saída"""
        filename = filedialog.asksaveasfilename(
            title="Salvar PDF como(save pdf as)",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_var.set(filename)
    
    def log(self, message: str):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def progress_callback(self, current: int, total: int, message: str):
        """Callback para atualizar progresso"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        self.log(message)
    
    def clear_fields(self):
        """Limpa todos os campos"""
        self.pdf_var.set("")
        self.book_var.set("")
        self.db_var.set("")
        self.output_var.set("")
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
    
    def process_highlights(self):
        """Processa os highlights em thread separada"""
        # Validar campos
        if not self.pdf_var.get() or not self.book_var.get() or not self.db_var.get():
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
        
        # Limpar log
        self.log_text.delete(1.0, tk.END)
        
        # Executar em thread separada
        thread = threading.Thread(target=self._process_highlights_thread)
        thread.daemon = True
        thread.start()
    
    def _process_highlights_thread(self):
        """Thread para processar highlights"""
        try:
            # Criar instância do highlighter
            self.highlighter = MoonHighlighter(
                self.pdf_var.get(),
                self.book_var.get(),
                self.db_var.get()
            )
            
            # Processar highlights
            output_file = self.highlighter.process_highlights(
                output_path=self.output_var.get() if self.output_var.get() else None,
                use_fuzzy=self.fuzzy_var.get(),
                progress_callback=self.progress_callback
            )
            
            if output_file:
                self.log(f"\n✅ Processamento concluído com sucesso!")
                self.log(f"📁 Arquivo de saída: {output_file}")
                messagebox.showinfo("Sucesso", f"PDF processado com sucesso!\nSalvo em: {output_file}")
            else:
                self.log(f"\n❌ Erro durante o processamento")
                messagebox.showerror("Erro", "Erro durante o processamento")
                
        except Exception as e:
            self.log(f"\n❌ Erro: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()


def main():
    """Função principal da aplicação"""
    parser = argparse.ArgumentParser(
        description="Moon Highlighter - Marca highlights em PDFs baseado em dados SQLite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python moon_highlighter.py -p livro.pdf -b "livro.pdf" -d pdfmarks.sqlite
  python moon_highlighter.py -p livro.pdf -b "livro.pdf" -d pdfmarks.sqlite -o livro_destacado.pdf
  python moon_highlighter.py --gui  # Abrir interface gráfica
        """
    )
    
    parser.add_argument(
        "-p", "--pdf", 
        help="Caminho para o arquivo PDF"
    )
    
    parser.add_argument(
        "-b", "--book", 
        help="Nome do livro no banco de dados"
    )
    
    parser.add_argument(
        "-d", "--database", 
        help="Caminho para o banco SQLite"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Caminho de saída para o PDF com highlights (opcional)"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Abrir interface gráfica"
    )
    
    parser.add_argument(
        "--no-fuzzy",
        action="store_true",
        help="Desabilitar busca fuzzy"
    )
    
    args = parser.parse_args()
    
    # Verificar se deve abrir GUI
    if args.gui:
        try:
            app = MoonHighlighterGUI()
            app.run()
        except Exception as e:
            print(f"Erro ao abrir interface gráfica: {e}")
            print("Certifique-se de que tkinter está instalado")
        return
    
    # Verificar argumentos obrigatórios para CLI
    if not args.pdf or not args.book or not args.database:
        print("Erro: Para uso via CLI, todos os argumentos são obrigatórios")
        print("Use --gui para abrir a interface gráfica")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Criar instância do MoonHighlighter
        highlighter = MoonHighlighter(args.pdf, args.book, args.database)
        
        # Processar highlights
        output_file = highlighter.process_highlights(
            args.output, 
            use_fuzzy=not args.no_fuzzy
        )
        
        if output_file:
            print(f"\nProcessamento concluído com sucesso!")
            print(f"Arquivo de saída: {output_file}")
            sys.exit(0)
        else:
            print("\nErro durante o processamento")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 