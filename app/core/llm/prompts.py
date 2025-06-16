from typing import List, Dict, Any
from app.schemas.ask import ConversationMessage

class PromptTemplates:
    """Templates and guidelines for the technical support agent."""
    
    SYSTEM_PROMPT = """Eres un asistente profesional de soporte técnico telefónico para empresas LATAM. Tu rol es guiar a los operadores paso a paso a través de sus problemas técnicos, basándote en los manuales técnicos de la empresa.

Directrices para interacción telefónica:
1. Mantén tus respuestas concisas y claras, optimizadas para comunicación verbal
2. Usa un lenguaje natural y conversacional, pero mantén el profesionalismo
3. Estructura tus respuestas para ser fácilmente entendibles por voz:
   - Comienza con una respuesta directa y breve
   - Divide las instrucciones en pasos numerados y cortos
   - Usa pausas naturales (indicadas con comas) para facilitar la comprensión
   - Confirma la comprensión del operador cuando sea necesario
4. Manejo de la conversación:
   - Si la pregunta no es clara, pide aclaración de manera amigable
   - Si necesitas más información, haz preguntas específicas
   - Confirma que el operador está siguiendo los pasos
   - Ofrece repetir información si es necesario
   - Mantén el contexto de la conversación y haz referencias a preguntas anteriores cuando sea relevante
5. Para información crítica:
   - Enfatiza advertencias de seguridad con frases como "IMPORTANTE" o "ATENCIÓN"
   - Pide confirmación explícita cuando sea necesario
   - Proporciona alternativas si un paso no funciona
6. Si no tienes la información en el contexto:
   - Indica claramente que no puedes responder
   - Sugiere generar un ticket de soporte

Recuerda: Tu objetivo es guiar al operador de manera clara y segura, considerando que la comunicación es por teléfono."""

    QUESTION_TEMPLATE = """Contexto del manual:
{context}

Historial de la conversación:
{conversation_history}

Pregunta actual del operador: {question}

Por favor, proporciona una respuesta clara y concisa, optimizada para comunicación telefónica. Si la información no está disponible en el contexto, indícalo y sugiere el siguiente paso apropiado."""

    ERROR_TEMPLATE = """Lo siento, pero encontré un problema al procesar tu pregunta. Te sugiero lo siguiente:

{fallback_text}

¿Podrías reformular tu pregunta o prefieres que te conecte con un supervisor técnico?"""

    @classmethod
    def format_question_prompt(cls, context: str, question: str, conversation_history: List[ConversationMessage] = None) -> List[Dict[str, str]]:
        """Format the prompt for a question with context and conversation history."""
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n".join([
                f"{'Operador' if msg.role == 'user' else 'Asistente'}: {msg.content}"
                for msg in conversation_history[-5:]  # Only include last 5 messages
            ])
        
        return [
            {"role": "system", "content": cls.SYSTEM_PROMPT},
            {"role": "user", "content": cls.QUESTION_TEMPLATE.format(
                context=context,
                conversation_history=history_text,
                question=question
            )}
        ]

    @classmethod
    def format_error_prompt(cls, fallback_text: str) -> str:
        """Format the prompt for an error response."""
        return cls.ERROR_TEMPLATE.format(fallback_text=fallback_text)

    @classmethod
    def format_context(cls, chunks: List[str]) -> str:
        """Format context chunks into a readable string."""
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            formatted_chunks.append(f"Sección {i}:\n{chunk}")
        return "\n\n".join(formatted_chunks) 