class TablePrompts:
    SYSTEM = "You are creating searchable descriptions for document retrieval."

    INSTRUCTION = """Generate a comprehensive, searchable description of a table.

Your description MUST cover:
1. Key facts, numbers, and data points
2. What the table measures or compares
3. Key trends or insights
4. Questions this table can answer
5. Alternative search terms

Prioritize retrieval quality over brevity."""


class ImagePrompts:
    SYSTEM = "You are creating searchable descriptions for document retrieval."

    INSTRUCTION = """Generate a comprehensive, searchable description of an image.

Your description MUST cover:
1. What is visually shown
2. Key data, labels, values
3. Concepts or processes
4. Questions this image can answer
5. Alternative search terms

Prioritize retrieval quality over brevity."""


class FormulaPrompts:
    SYSTEM = "You are creating searchable descriptions for document retrieval."

    INSTRUCTION = """Generate a comprehensive, searchable description of a formula.

Your description MUST cover:
1. What it represents
2. Meaning of variables
3. When it is used
4. Questions it can answer
5. Alternative search terms

Prioritize retrieval quality over brevity."""


class RAGPrompts:
    ANSWER = """You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question:
{query}

Answer:"""


class SearchableDescriptionPrompts:
    SYSTEM = "You are creating a searchable description for document content retrieval."

    @staticmethod
    def build_prompt_text(text: str, tables: list[str], images: list[str]) -> str:
        prompt_text = f"""You are creating a searchable description for document content retrieval.

CONTENT TO ANALYZE:
TEXT CONTENT:
{text}
"""

        if tables:
            prompt_text += "\nTABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"Table {i+1}:\n{table}\n\n"

        if images:
            prompt_text += "\nIMAGES:\n"
            for i in range(len(images)):
                prompt_text += f"Image {i+1}: base64 image content available\n"

        prompt_text += """
YOUR TASK:
Generate a comprehensive, searchable description that covers:

1. Key facts, numbers, and data points from text and tables
2. Main topics and concepts discussed
3. Questions this content could answer
4. Visual content analysis (charts, diagrams, patterns in images)
5. Alternative search terms users might use

Write in plain paragraphs without any markdown formatting.
Do not use **bold**, *italic*, bullet points, or any special characters for emphasis.
Separate each section with a blank line (\n\n).
Use plain section labels like \"Key Facts:\" instead of \"**Key Facts:**\".

Make it detailed and searchable - prioritize findability over brevity.

SEARCHABLE DESCRIPTION:
"""
        return prompt_text