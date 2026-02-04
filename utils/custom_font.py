"""
Custom Font Manager - Sistema de glyphs customizados para displays
Permite renderizar caracteres Unicode especiais em displays com charset limitado
"""

import framebuf

# Custom font glyphs (8x8 pixels, 1 bit per pixel)
# Cada glyph são 8 bytes representando 8 linhas de 8 pixels
CUSTOM_GLYPHS = {
    # Caracteres Português - UTF-8
    '°': [  # Grau
        0b00011000,  #   **  
        0b00100100,  #  *  * 
        0b01000010,  # *    *
        0b01000010,  # *    *
        0b00100100,  #  *  * 
        0b00011000,  #   **  
        0b00000000,  #       
        0b00000000   #       
    ],
    'ã': [  # a til
        0b00011000,  #   **  
        0b00100100,  #  *  * 
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'á': [  # a agudo
        0b00001000,  #    *  
        0b00011000,  #   **  
        0b00100100,  #  *  * 
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'â': [  # a circunflexo
        0b00100100,  #  *  * 
        0b01000010,  # *    *
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'é': [  # e agudo
        0b00001000,  #    *  
        0b00011000,  #   **  
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'ê': [  # e circunflexo
        0b00100100,  #  *  * 
        0b01000010,  # *    *
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'í': [  # i agudo
        0b00001000,  #    *  
        0b00011000,  #   **  
        0b00111100,  #   ****
        0b00001000,  #    *  
        0b00001000,  #    *  
        0b01111100,  #  **** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'ó': [  # o agudo
        0b00001000,  #    *  
        0b00011000,  #   **  
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'ô': [  # o circunflexo
        0b00100100,  #  *  * 
        0b01000010,  # *    *
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'õ': [  # o til
        0b00011000,  #   **  
        0b00100100,  #  *  * 
        0b01111110,  # ****** 
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'ú': [  # u agudo
        0b00001000,  #    *  
        0b00011000,  #   **  
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b10000001,  # *      *
        0b01111110,  # ****** 
        0b00000000,  #       
        0b00000000   #       
    ],
    'ç': [  # c cedilha
        0b00000000,  #       
        0b01111100,  #  **** 
        0b10000010,  # *    * 
        0b10000000,  # *     
        0b10000010,  # *    * 
        0b01111100,  #  **** 
        0b00101000,  #   * * 
        0b00010000   #    *  
    ],
    
    # Símbolos especiais
    '♥': [  # Coração
        0b00000000,  #       
        0b01100110,  #  **  **
        0b11111111,  # ********
        0b11111111,  # ********
        0b01111110,  #  ******
        0b00111100,  #   **** 
        0b00011000,  #   **  
        0b00000000   #       
    ],
    '°': [  # Grau (alternativo mais fino)
        0b00011000,  #   **  
        0b00100100,  #  *  * 
        0b00100100,  #  *  * 
        0b00011000,  #   **  
        0b00000000,  #       
        0b00000000,  #       
        0b00000000,  #       
        0b00000000   #       
    ],
    '±': [  # Mais ou menos
        0b00010000,  #    *  
        0b00010000,  #    *  
        0b11111110,  # *******
        0b00010000,  #    *  
        0b00010000,  #    *  
        0b00000000,  #       
        0b00000000   #       
    ],
}


class CustomFontManager:
    """Gerenciador de font customizadas para displays"""
    
    def __init__(self):
        self.glyphs = CUSTOM_GLYPHS
        self.enabled = True
    
    def has_glyph(self, char):
        """Verifica se existe glyph para o caractere"""
        return char in self.glyphs
    
    def get_glyph(self, char):
        """Retorna o glyph para o caractere"""
        return self.glyphs.get(char)
    
    def draw_char(self, framebuffer, char, x, y, color=1):
        """
        Desenha um caractere customizado no framebuffer
        framebuffer: instância de FrameBuffer
        char: caractere a desenhar
        x, y: posição superior esquerda
        color: cor (1=branco, 0=preto)
        """
        glyph = self.get_glyph(char)
        if not glyph:
            return False
        
        for row, bits in enumerate(glyph):
            for col in range(8):
                if bits & (1 << (7 - col)):
                    if hasattr(framebuffer, 'pixel'):
                        framebuffer.pixel(x + col, y + row, color)
        return True
    
    def draw_text(self, framebuffer, text, x, y, color=1):
        """
        Desenha texto com suporte a glyphs customizados
        Lógica por caractere (corrigida para 8px total):
        - Se tem glyph customizado: usa draw_char() (8x8 pixels)
        - Se é ASCII (< 128): usa text() padrão + espaçamento
        - Se não tem glyph: tratamento especial
        """
        current_x = x
        
        for char in text:
            char_code = ord(char)
            
            if self.has_glyph(char) and self.enabled:
                # 1. Tem glyph customizado -> usa glyph (8x8 completo)
                self.draw_char(framebuffer, char, current_x, y, color)
                current_x += 8  # Glyph já ocupa 8px completo
                
            elif char_code < 128:
                # 2. ASCII padrão -> usa text() + espaçamento manual
                if hasattr(framebuffer, 'text'):
                    framebuffer.text(char, current_x + 1, y + 1, color)  # Centro do espaço 8x8
                    current_x += 8  # Espaço total de 8px por caractere
                else:
                    # Fallback se framebuffer não tiver text()
                    current_x += 8
                    
            else:
                # 3. Unicode sem glyph -> placeholder no espaço 8x8
                self._handle_missing_glyph(framebuffer, char, current_x, y, color)
                current_x += 8  # Espaço total de 8px
        
        return current_x - x
    
    def _handle_missing_glyph(self, framebuffer, char, x, y, color):
        """
        Trata caracteres que não têm glyph customizado
        Placeholder centralizado no espaço 8x8
        """
        # Desenha placeholder centralizado (quadrado 4x4 no meio do espaço 8x8)
        center_x = x + 2  # Centro do espaço 8x8
        center_y = y + 2
        
        for dx in range(4):
            for dy in range(4):
                if dx == 0 or dx == 3 or dy == 0 or dy == 3:
                    if hasattr(framebuffer, 'pixel'):
                        framebuffer.pixel(center_x + dx, center_y + dy, color)
    
    def analyze_text_support(self, text):
        """
        Analisa um texto e retorna detalhes sobre o suporte
        Retorna: {
            'total_chars': int,
            'ascii_chars': int,
            'custom_glyphs': int,
            'missing_chars': int,
            'missing_list': [str],
            'fully_supported': bool
        }
        """
        result = {
            'total_chars': len(text),
            'ascii_chars': 0,
            'custom_glyphs': 0,
            'missing_chars': 0,
            'missing_list': [],
            'fully_supported': True
        }
        
        for char in text:
            char_code = ord(char)
            
            if self.has_glyph(char):
                result['custom_glyphs'] += 1
            elif char_code < 128:
                result['ascii_chars'] += 1
            else:
                result['missing_chars'] += 1
                result['missing_list'].append(char)
                result['fully_supported'] = False
        
        return result
    
    def get_text_width(self, text):
        """
        Calcula a largura do texto considerando espaçamento 8px por caractere
        """
        width = 0
        for char in text:
            if self.has_glyph(char) and self.enabled:
                width += 8  # Glyphs customizados já ocupam 8px completo
            else:
                width += 8  # ASCII também ocupa 8px total (6px + 1px cada lado)
        return width
    
    def is_text_supported(self, text):
        """
        Verifica se todos os caracteres do texto têm suporte
        (têm glyph ou são ASCII básico)
        """
        for char in text:
            if ord(char) > 127 and not self.has_glyph(char):
                return False
        return True
    
    def enable(self):
        """Ativa o uso de glyphs customizados"""
        self.enabled = True
    
    def disable(self):
        """Desativa o uso de glyphs customizados"""
        self.enabled = False
    
    def add_glyph(self, char, glyph_data):
        """
        Adiciona um novo glyph customizado
        char: caractere
        glyph_data: lista de 8 bytes (8 linhas de 8 pixels)
        """
        if len(glyph_data) == 8 and all(isinstance(row, int) and 0 <= row <= 255 for row in glyph_data):
            self.glyphs[char] = glyph_data
            return True
        return False


# Instância global
_custom_font = None


def get_custom_font():
    """Retorna a instância global do gerenciador de fontes customizadas"""
    global _custom_font
    if _custom_font is None:
        _custom_font = CustomFontManager()
    return _custom_font


def draw_custom_text(framebuffer, text, x, y, color=1):
    """
    Função de atalho para desenhar texto com font customizada
    """
    font = get_custom_font()
    return font.draw_text(framebuffer, text, x, y, color)


def has_custom_support(char):
    """
    Função de atalho para verificar se caractere tem suporte customizado
    """
    font = get_custom_font()
    return font.has_glyph(char)