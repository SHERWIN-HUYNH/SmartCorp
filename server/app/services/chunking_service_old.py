import uuid
from typing import List, Optional


from app.services.LLM_service import LLMService
from app.services.cloudflare_service import CloudflareR2Service


class ChunkingService:
    """Xử lý logic chunking từ elements"""

    SKIP_TYPES = {
        "Address", "Header", "Footer",
        "UncategorizedText", "PageBreak"
    }

    def __init__(self, min_text_length: int = 100, cloudflare_service: Optional[CloudflareR2Service] = None):
        self.current_title: Optional[str] = None
        self.current_title_id: Optional[str] = None
        self.chunks: List[dict] = []
        self.current_order: int = 0
        self.last_visual_chunk_idx: Optional[int] = None  # index của Image/Table chunk cuối
        self.MIN_TEXT_LENGTH = min_text_length
        self.cloudflare_service = cloudflare_service
        self.upload_enabled = cloudflare_service is not None

    def reset(self):
        self.current_title = None
        self.current_title_id = None
        self.chunks = []
        self.current_order = 0
        self.last_visual_chunk_idx = None

    def _base_chunk(self, text: str, chunk_type: str, page: int) -> dict:
        chunk = {
            "id": str(uuid.uuid4()),
            "text": text,
            "type": chunk_type,
            "page": page,
            "parent_id": self.current_title_id,
            "title": self.current_title,
            "order": self.current_order,
        }

        self.current_order += 1
        return chunk

    def _handle_title(self, element):
        self.current_title = element.text.strip()
        self.current_title_id = element.id
        self.last_visual_chunk_idx = None   # reset khi sang title mới
        self.current_order = 0

    def _handle_narrative_text(self, element):
        text = element.text.strip()
        if not text:
            return

        # Nếu text ngắn và chunk trước cùng title → gộp vào
        if (
            len(text) < self.MIN_TEXT_LENGTH
            and self.chunks
            and self.chunks[-1]["type"] in ("NarrativeText", "ListItem")
            and self.chunks[-1]["parent_id"] == self.current_title_id
        ):
            self.chunks[-1]["text"] += f"\n{text}"
            return

        chunk = self._base_chunk(text, "NarrativeText", element.metadata.page_number)
        self.chunks.append(chunk)

    def _handle_list_item(self, element):
        text = element.text.strip()
        if not text:
            return

        if (
            self.chunks
            and self.chunks[-1]["type"] == "ListItem"
            and self.chunks[-1]["parent_id"] == self.current_title_id
        ):
            self.chunks[-1]["text"] += f"\n• {text}"
        else:
            chunk = self._base_chunk(f"• {text}", "ListItem", element.metadata.page_number)
            self.chunks.append(chunk)

    def _handle_figure_caption(self, element):
        """Gán caption vào Image/Table chunk trước đó"""
        text = element.text.strip()
        if not text:
            return

        if self.last_visual_chunk_idx is not None:
            self.chunks[self.last_visual_chunk_idx]["text"] += f"\nCaption: {text}"
        else:
            # Không có visual trước đó → treat như NarrativeText
            chunk = self._base_chunk(text, "FigureCaption", element.metadata.page_number)
            self.chunks.append(chunk)

    def _get_context_text(self) -> str:
        """Lấy toàn bộ text chunks trong cùng title hiện tại"""
        text_chunks = [
            c for c in self.chunks
            if c["parent_id"] == self.current_title_id
            and c["type"] in ("NarrativeText", "ListItem", "Formula")
        ]
        return "\n\n".join(c["text"] for c in text_chunks) if text_chunks else ""


    def _handle_table(self, element, llm_service: "LLMService"):
        raw_html = element.metadata.text_as_html or ""
        # context = self._get_context_text()
        description = llm_service.describe_table(raw_html, '')

        chunk = self._base_chunk(description, "Table", element.metadata.page_number)
        
        # Upload HTML table to Cloudflare R2 và lưu URL
        if self.upload_enabled and raw_html:
            try:
                table_url = self.cloudflare_service.upload_html_table(
                    raw_html,
                    filename=f"table_{element.id}.html"
                )
                chunk["table_url"] = table_url
                # Không lưu raw_table nữa, chỉ lưu URL
            except Exception as e:
                print(f"Warning: Failed to upload table to R2: {e}")
                # Fallback: keep raw_table nếu upload fails
                chunk["raw_table"] = raw_html
        else:
            chunk["raw_table"] = raw_html

        self.chunks.append(chunk)
        self.last_visual_chunk_idx = len(self.chunks) - 1


    def _handle_image(self, element, llm_service: "LLMService"):
        image_b64 = element.metadata.image_base64 or ""
        # context = self._get_context_text()
        description = llm_service.describe_image(image_b64, '')

        chunk = self._base_chunk(description, "Image", element.metadata.page_number)
        
        # Upload base64 image to Cloudflare R2 và lưu URL
        if self.upload_enabled and image_b64:
            try:
                image_url = self.cloudflare_service.upload_image_from_base64(
                    image_b64,
                    filename=f"image_{element.id}.png"
                )
                chunk["image_url"] = image_url
                # Không lưu image_b64 nữa, chỉ lưu URL
            except Exception as e:
                print(f"Warning: Failed to upload image to R2: {e}")
                # Fallback: keep image_b64 nếu upload fails
                chunk["image_b64"] = image_b64
        else:
            chunk["image_b64"] = image_b64

        self.chunks.append(chunk)
        self.last_visual_chunk_idx = len(self.chunks) - 1

    def _handle_formula(self, element, llm_service: "LLMService"):
        text = element.text.strip()
        if not text:
            return
        
        # context = self._get_context_text()
        # description = llm_service.describe_formula(text, context=context)

        # chunk = self._base_chunk(description, "Formula", element.metadata.page_number)

        chunk = self._base_chunk(text, "Formula", element.metadata.page_number)
        
        chunk["raw_formula"] = text
        self.chunks.append(chunk)

    def chunking(self, elements, llm_service: "LLMService") -> List[dict]:
        self.reset()

        for element in elements:
            element_type = element.category

            if element_type in self.SKIP_TYPES:
                continue

            elif element_type == "Title":
                self._handle_title(element)

            elif element_type == "NarrativeText":
                self._handle_narrative_text(element)

            elif element_type == "ListItem":
                self._handle_list_item(element)

            elif element_type == "FigureCaption":
                self._handle_figure_caption(element)

            elif element_type == "Table":
                self._handle_table(element, llm_service)

            elif element_type == "Image":
                self._handle_image(element, llm_service)

            elif element_type == "Formula":
                self._handle_formula(element, llm_service)

            # else: bỏ qua tất cả types còn lại

        print(f"{len(self.chunks)} chunks created")
        return self.chunks