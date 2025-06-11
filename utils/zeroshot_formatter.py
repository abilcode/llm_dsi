import re
from langchain.prompts import PromptTemplate


class ZeroShotTextFormatter:
    """
    Zero-shot formatter untuk merapihkan output text tanpa mengubah konten.
    Fokus pada formatting visual: spacing, line breaks, bullet points, dll.
    """

    def __init__(self, use_llm: bool = True, model_name: str = "gpt-4.1-mini"):
        self.use_llm = use_llm
        if use_llm:
            from langchain.chat_models import ChatOpenAI
            self.llm = ChatOpenAI(model=model_name, temperature=0)
            self._setup_formatter_prompt()

    def _setup_formatter_prompt(self):
        """Setup prompt untuk zero-shot formatting"""
        self.formatter_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Tugas: Rapihkan format text berikut TANPA mengubah konten atau makna.

ATURAN KETAT:
1. JANGAN ubah, tambah, atau hapus informasi apapun
2. JANGAN ubah urutan informasi 
3. HANYA perbaiki format visual (spacing, line breaks, indentasi)
4. Buat list menjadi rapi dengan bullet points atau numbering
5. Pisahkan paragraf dengan line break yang tepat
6. Perbaiki spacing yang tidak konsisten
7. Jika user menanyakan terkait dengan cara memesan kamar, jawab dengan "Anda dapat langsung memesan kamar dengan menyebutkan nomor kamar yang diinginkan dan kemudian melakukan pembayaran dari link yang akan dikirim kepada anda."

CONTOH BEFORE/AFTER:

BEFORE:
"Berdasarkan data kamar yang tersedia: R001 available level_1 standard, R003 available level_1 deluxe,R005 occupied level_2 standard"

AFTER:
"Berdasarkan data kamar yang tersedia:
• R001 - available, level 1, standard
• R003 - available, level 1, deluxe  
• R005 - occupied, level 2, standard"

BEFORE:
"Untuk keluhan Anda: 1.Isi nama lengkap 2.Nomor kamar 3.Deskripsi masalah    kemudian submit"

AFTER:
"Untuk keluhan Anda:
1. Isi nama lengkap
2. Nomor kamar
3. Deskripsi masalah

- Balikan Dokumen Penjelasan Detail Kamar: ``` https://drive.google.com/file/d/1tjETJ4pRF0A8wvy6MArWJvq2_p2E1i_D/view?usp=sharing ```
- Balikan Dokumen Pembayaran Detail Kamar: ``` https://drive.google.com/file/d/1gl1zWZfmfcv06LVNPDOBjERf9avkBko2/view?usp=sharing ```
- Balikan Dokumen Tata Tertib Detail Kamar: ``` https://drive.google.com/file/d/1VwC6hu0h_Jymknvwl1asRmsx_0tE6QqO/view?usp=sharing ```

Kalau text yang diperlukan dirapikan memuat URL, pastikan give AS IS URL.

Kemudian submit."

Text yang perlu dirapihkan:
{text}

Text yang sudah dirapihkan (konten sama, format lebih baik):"""
        )

    def format_text(self, text: str) -> str:
        """
        Main method untuk memformat text

        Args:
            text (str): Text mentah yang perlu dirapihkan

        Returns:
            str: Text yang sudah diformat dengan rapi
        """
        if not text or not text.strip():
            return text

        # Coba LLM formatter dulu jika tersedia
        if self.use_llm:
            try:
                formatted = self._llm_format(text)
                if formatted and self._is_valid_format(formatted, text):
                    return formatted
            except Exception:
                pass  # Fallback ke rule-based

        # Fallback ke rule-based formatting
        return self._rule_based_format(text)

    def _llm_format(self, text: str) -> str:
        """Format menggunakan LLM dengan zero-shot prompt"""
        if not hasattr(self, 'llm'):
            return text

        formatted = self.llm.predict(self.formatter_prompt.format(text=text))
        return formatted.strip()

    def _rule_based_format(self, text: str) -> str:
        """
        Rule-based formatting sebagai fallback
        Implementasi sederhana tanpa LLM
        """
        if not text:
            return text

        formatted = text

        # 1. Basic whitespace cleanup
        formatted = self._clean_whitespace(formatted)

        # 2. Format lists dan enumerations
        formatted = self._format_lists(formatted)

        # 3. Format data sequences (comma-separated values)
        formatted = self._format_data_sequences(formatted)

        # 4. Add proper paragraph breaks
        formatted = self._add_paragraph_breaks(formatted)

        # 5. Final cleanup
        formatted = self._final_cleanup(formatted)

        return formatted

    def _clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace"""
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)

        # Clean spaces around punctuation
        text = re.sub(r' +([,.!?:;])', r'\1', text)
        text = re.sub(r'([,.!?:;]) +', r'\1 ', text)

        # Remove trailing whitespace from lines
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)

        return text

    def _format_lists(self, text: str) -> str:
        """Format berbagai jenis list menjadi rapi"""

        # Format numbered lists (1.something 2.something)
        text = re.sub(r'(\d+)\.([^\d])', r'\1. \2', text)
        text = re.sub(r'(\d+\.[^.]*?)(\d+\.)', r'\1\n\2', text)

        # Format comma-separated numbered items
        text = re.sub(r'(\d+\.[^,]*),\s*(\d+\.)', r'\1\n\2', text)

        # Format items yang dipisah dengan koma tapi bisa jadi list
        # Pattern: "item1, item2, item3" -> list format
        comma_list_pattern = r'([A-Z][^,]{10,}),\s*([A-Z][^,]{10,}),\s*([A-Z][^,]{10,})'
        if re.search(comma_list_pattern, text):
            def replace_comma_list(match):
                items = [item.strip() for item in match.group(0).split(',')]
                return '\n• ' + '\n• '.join(items)

            text = re.sub(comma_list_pattern, replace_comma_list, text)

        return text

    def _format_data_sequences(self, text: str) -> str:
        """Format data sequences seperti room data, dll"""

        # Pattern untuk room data: "R001 available level_1 standard"
        room_pattern = r'(R\d+)\s+(\w+)\s+(level_\d+)\s+(\w+)'

        def format_room_data(match):
            room_id, status, level, room_type = match.groups()
            level_num = level.replace('level_', '')
            return f"• {room_id} - {status}, level {level_num}, {room_type}"

        text = re.sub(room_pattern, format_room_data, text)

        # Format comma-separated room data
        if 'R0' in text and ('available' in text or 'occupied' in text):
            # Jika ada beberapa room data yang dipisah koma
            room_data_pattern = r'(R\d+[^,]*(?:available|occupied)[^,]*)'
            rooms = re.findall(room_data_pattern, text)
            if len(rooms) > 1:
                # Replace with formatted list
                original = ', '.join(rooms)
                formatted_rooms = []
                for room in rooms:
                    # Apply room formatting to each
                    formatted_room = re.sub(
                        room_pattern, format_room_data, room)
                    if not formatted_room.startswith('•'):
                        formatted_room = '• ' + formatted_room
                    formatted_rooms.append(formatted_room)

                if original in text:
                    text = text.replace(original, '\n'.join(formatted_rooms))

        return text

    def _add_paragraph_breaks(self, text: str) -> str:
        """Add proper paragraph breaks"""

        # Add break before "Untuk", "Silakan", "Berdasarkan" jika tidak di awal
        section_starters = ['Untuk', 'Silakan',
                            'Berdasarkan', 'Jika', 'Apabila']
        for starter in section_starters:
            pattern = r'([.!?])\s*(' + starter + r')'
            text = re.sub(pattern, r'\1\n\n\2', text)

        # Add break after colons before lists
        text = re.sub(r':\s*([•\d])', r':\n\1', text)

        return text

    def _final_cleanup(self, text: str) -> str:
        """Final cleanup"""

        # Remove excessive line breaks (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Ensure proper spacing around bullets
        text = re.sub(r'\n•', '\n• ', text)
        text = re.sub(r'\n• +', '\n• ', text)

        # Ensure proper spacing around numbers
        text = re.sub(r'\n(\d+\.)', r'\n\1 ', text)
        text = re.sub(r'\n(\d+\.) +', r'\n\1 ', text)

        return text.strip()

    def _is_valid_format(self, formatted_text: str, original_text: str) -> bool:
        """
        Validasi apakah hasil formatting masih preserve konten asli
        """
        # Simple validation: check jika tidak ada konten yang hilang drastis
        original_words = set(re.findall(r'\w+', original_text.lower()))
        formatted_words = set(re.findall(r'\w+', formatted_text.lower()))

        # Jika lebih dari 10% kata hilang, kemungkinan ada masalah
        if len(formatted_words) < len(original_words) * 0.9:
            return False

        # Check jika ada kata-kata penting yang hilang
        important_words = {'kamar', 'room', 'keluhan',
                           'pembayaran', 'tersedia', 'available'}
        original_important = important_words.intersection(original_words)
        formatted_important = important_words.intersection(formatted_words)

        return len(formatted_important) >= len(original_important)


# Integration dengan main agent
class FormattedMainAgent:
    """
    Wrapper untuk main agent yang menambahkan formatting
    """

    def __init__(self, main_agent, use_llm_formatter: bool = True):
        self.main_agent = main_agent
        self.formatter = ZeroShotTextFormatter(use_llm=use_llm_formatter)

    def run(self, query: str, user_id: int) -> str:
        """
        Run main agent dengan post-processing formatting
        """
        # Get raw response from main agent
        raw_response = self.main_agent.run(query, user_id)

        # Format the response
        formatted_response = self.formatter.format_text(raw_response)

        return formatted_response


# Contoh penggunaan
def demo_formatter():
    """Demo cara menggunakan formatter"""

    formatter = ZeroShotTextFormatter(
        use_llm=False)  # Pure rule-based untuk demo

    test_cases = [
        # Case 1: Messy room data
        "Berdasarkan data kamar: R001 available level_1 standard,R003 available level_1 deluxe,R005 occupied level_2 standard",

        # Case 2: Messy numbered list
        "Untuk mengajukan keluhan: 1.Isi nama lengkap 2.Nomor kamar 3.Deskripsi masalah    kemudian submit ke sistem",

        # Case 3: Mixed formatting issues
        "Peraturan guest house:jam malam sampai 23.00 WIB,dilarang merokok,maksimal 1 orang per kamar.   Silakan patuhi aturan ini.",

        # Case 4: Complex response
        "Keluhan berhasil disimpan dengan ID: 123.Tim akan menangani keluhan Anda.Untuk pertanyaan lain hubungi: 1.Front desk 2.WhatsApp 3.Email support"
    ]

    print("🧪 Demo Zero-Shot Text Formatter")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print("BEFORE:")
        print(f'"{test_case}"')

        formatted = formatter.format_text(test_case)

        print("\nAFTER:")
        print(f'"{formatted}"')
        print("-" * 40)


if __name__ == "__main__":
    demo_formatter()
