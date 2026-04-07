import uuid
import json
from openai import OpenAI
from typing import List, Optional
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from app.core.prompt import SearchableDescriptionPrompts
from app.services.cloudflare_service import CloudflareR2Service


class ChunkingService:
    def __init__(self, client: OpenAI, min_element_length: int = 100, use_hard_max_length_characters: bool = True, verbose=True):
        self.client = client
        self.min_element_length = min_element_length
        self.use_hard_max_length_characters = use_hard_max_length_characters
        self.split_character = '<<SPLIT>>'
        self.verbose = verbose
        self.cloudflare_service: Optional[CloudflareR2Service] = None
        self.upload_enabled = False
        self._init_cloudflare_upload()

    def _init_cloudflare_upload(self):
        try:
            self.cloudflare_service = CloudflareR2Service()
            self.upload_enabled = True
            if self.verbose:
                print("Cloudflare R2 upload is enabled")
        except Exception as e:
            self.upload_enabled = False
            self.cloudflare_service = None
            if self.verbose:
                print(f"Cloudflare R2 upload disabled: {e}")

    def _upload_tables_to_cloudflare(self, tables: List[str], chunk_index: int) -> List[str]:
        if not self.upload_enabled or not self.cloudflare_service:
            return []

        uploaded_urls = []
        for table_idx, table_html in enumerate(tables):
            if not table_html:
                continue

            try:
                table_url = self.cloudflare_service.upload_html_table(
                    table_html,
                    filename=f"tables/chunk_{chunk_index}_{table_idx}.html",
                )
                uploaded_urls.append(table_url)
            except Exception as e:
                if self.verbose:
                    print(f"Table upload failed at chunk {chunk_index}, index {table_idx}: {e}")

        return uploaded_urls

    def _upload_images_to_cloudflare(self, images: List[str], chunk_index: int) -> List[str]:
        if not self.upload_enabled or not self.cloudflare_service:
            return []

        uploaded_urls = []
        for image_idx, image_b64 in enumerate(images):
            if not image_b64:
                continue

            try:
                image_url = self.cloudflare_service.upload_image_from_base64(
                    image_b64,
                    filename=f"images/chunk_{chunk_index}_{image_idx}.png",
                )
                uploaded_urls.append(image_url)
            except Exception as e:
                if self.verbose:
                    print(f"Image upload failed at chunk {chunk_index}, index {image_idx}: {e}")

        return uploaded_urls


    def _partition_document(self, file_path: str):
        """Extract elements from PDF using unstructured"""
        if self.verbose:
            print(f"Partitioning document: {file_path}")
        
        elements = partition_pdf(
            filename=file_path,  # Path to your PDF file
            strategy="hi_res", # Use the most accurate (but slower) processing method of extraction
            infer_table_structure=True, # Keep tables as structured HTML, not jumbled text
            extract_image_block_types=["Image"], # Grab images found in the PDF
            extract_image_block_to_payload=True # Store images as base64 data you can actually use
        )

        for element in elements:
            if hasattr(element, "text"):
                element.text = (element.text or "") + self.split_character

        if self.verbose:
            print(f"Extracted {len(elements)} elements")

        return elements
    
    def _create_chunks_by_title(self, elements):
        """Create chunks using title-based strategy"""
        if self.verbose:
            print("Creating chunks by title...")
        
        filtered_elements = [
            el for el in elements 
            if el.category not in ("FigureCaption", "PageBreak", "Footer", "Header")
        ]

        for el in filtered_elements:
            if el.category in ("Table", "Image"):
                el.text = ""


        max_characters = 3000

        if not self.use_hard_max_length_characters:
            for el in filtered_elements:
                if len(el.text) > max_characters:
                    max_characters = len(el.text)
        
        
        chunks = chunk_by_title(
            filtered_elements,
            max_characters=max_characters,
            new_after_n_chars=2400,
            combine_text_under_n_chars=500
        )
        
        if self.verbose:
            print(f"Created {len(chunks)} chunks")

        return chunks
    


    def _separate_content_types(self, chunk):
        metadata = chunk.metadata.to_dict()

        content_data = {
            'text': chunk.text,
            'page_number': metadata.get('page_number'),
            'tables': [],
            'images': [],
            'types': ['text']
        }
        
        if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
            for element in chunk.metadata.orig_elements:
                element_type = type(element).__name__
                
                if element_type == 'Table':
                    content_data['types'].append('table')
                    table_html = getattr(element.metadata, 'text_as_html', element.text)
                    content_data['tables'].append(table_html)
                
                elif element_type == 'Image':
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                        content_data['types'].append('image')
                        content_data['images'].append(element.metadata.image_base64)
        
        content_data['types'] = list(set(content_data['types']))
        return content_data


    def _create_ai_enhanced_summary(self, text: str, tables: List[str], images: List[str]) -> str:
        try:
            prompt_text = SearchableDescriptionPrompts.build_prompt_text(text, tables, images)

            content = [
                {
                    "type": "input_text",
                    "text": prompt_text
                }
            ]

            for image_base64 in images:
                content.append({
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                })

            response = self.client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0
            )

            return response.output_text

        except Exception as e:
            print(f"AI summary failed: {e}")
            summary = f"{text[:300]}..."
            if tables:
                summary += f" [Contains {len(tables)} table(s)]"
            if images:
                summary += f" [Contains {len(images)} image(s)]"
            return summary


    def _summarise_chunks(self, chunks):
        if self.verbose:
            print('Summary Chunks...')

        documents = []
        
        for i, chunk in enumerate(chunks):
            content_data = self._separate_content_types(chunk)
            table_urls = self._upload_tables_to_cloudflare(content_data['tables'], i)
            image_urls = self._upload_images_to_cloudflare(content_data['images'], i)
            
            
            if content_data['tables'] or content_data['images']:
                try:
                    enhanced_content = self._create_ai_enhanced_summary(
                        content_data['text'],
                        content_data['tables'], 
                        content_data['images']
                    )
                except Exception as e:
                    print(f"AI summary failed: {e}")
                    enhanced_content = content_data['text']
            else:
                enhanced_content = content_data['text']
            
            doc = {
                "page_content": enhanced_content,
                "metadata": {
                    "original_content": json.dumps({
                        "type": content_data['types'],
                        "page": content_data['page_number'],
                        "raw_text": content_data['text'],
                        "tables_html": content_data['tables'],
                        "images_base64": content_data['images'],
                        "table_urls": table_urls,
                        "image_urls": image_urls,
                    })
                }
            }
            
            documents.append(doc)
        
        print(f"Processed {len(documents)} chunks")
        return documents


    def _split_chunk(self, processed_chunks):
        all_chunks = []
        for i in range (len(processed_chunks)):
            original_content = processed_chunks[i].get('metadata', {}).get('original_content', '{}')
            original_content = json.loads(original_content)
            page_content = processed_chunks[i].get('page_content', '')

            small_chunks = self._get_small_chunks(original_content, page_content)
            all_chunks.extend(small_chunks)

        return all_chunks


    def _get_small_chunks(self, original_content, page_content):
        small_chunks = []

        raw_text = original_content.get('raw_text', '')
        split_texts = [text.strip() for text in raw_text.split(self.split_character) if text.strip()]

        if not split_texts:
            return small_chunks

        split_texts = self._merge_short_texts(split_texts)

        page = int(original_content.get('page', 0) or 0)
        parent_id = str(uuid.uuid4())
        order = 0
        title = split_texts[0]
        table_html = original_content.get('tables_html', [])
        image_base64 = original_content.get('images_base64', [])
        table_urls = original_content.get('table_urls', [])
        image_urls = original_content.get('image_urls', [])

        for text in split_texts[1:]:
            chunk = {
                'title': title,
                'text': text,
                'type': 'text',
                'page': page,
                'parent_id': parent_id,
                'order': order,
            }

            small_chunks.append(chunk)
            order += 1

        if table_html:
            chunk = {
                'title': title,
                'text': page_content,
                'type': 'table',
                'page': page,
                'parent_id': parent_id,
                'order': order,
                'raw_table': table_html,
            }
            if table_urls:
                chunk['table_url'] = table_urls
            small_chunks.append(chunk)

        elif image_base64:
            chunk = {
                'title': title,
                'text': page_content,
                'type': 'image',
                'page': page,
                'parent_id': parent_id,
                'order': order,
                'image_b64': image_base64,
            }
            if image_urls:
                chunk['image_url'] = image_urls
            small_chunks.append(chunk)

        return small_chunks


    def _merge_short_texts(self, splited_texts):
        result = []

        for text in splited_texts:
            if len(text) < self.min_element_length and result:
                result[-1] += " " + text
            else:
                result.append(text)

        return result

    def partition_document(self, file_path: str):
        return self._partition_document(file_path)

    def create_chunks_by_title(self, elements):
        return self._create_chunks_by_title(elements)

    def summarise_chunks(self, chunks):
        return self._summarise_chunks(chunks)

    def split_chunks(self, processed_chunks):
        return self._split_chunk(processed_chunks)

    def ingestion_pdf(self, file_path, document_id: str, role_allowed: List[str]):
        raise NotImplementedError(
            "ChunkingService no longer performs ingestion. "
            "Use IngestionService.ingest_pdf(...) instead."
        )
