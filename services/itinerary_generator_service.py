# services/itinerary_generator_service.py
import json
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import TypedDict

class ItineraryGeneratorService:
    """
    Serviço dedicado a receber os dados coletados e gerar o roteiro final
    através de uma chamada de Chat Completion.
    """
    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.7
    MAX_TOKENS = 3500

    def __init__(self, client: AsyncOpenAI):
        self.client = client

    def _get_generator_prompt(self, itinerary_data: dict) -> str:
        """Cria o prompt de sistema para a fase de GERAÇÃO do roteiro."""
        data_str = json.dumps(itinerary_data, indent=2, ensure_ascii=False)
        
        return f"""Você é um especialista em viagens para Orlando. Sua única tarefa é pegar os dados do cliente em formato JSON e transformá-los em um roteiro de viagem detalhado, dia a dia, em português do Brasil.

# DADOS DO CLIENTE:
{data_str}

# REGRAS DE GERAÇÃO:
- Crie um roteiro dia a dia, começando pela data de chegada.
- Use subtítulos em negrito para cada dia (ex: **Dia 1: Chegada e Disney Springs**).
- Para cada dia, use uma lista de marcadores (bullets) para as atividades, incluindo horários sugeridos.
- Incorpore dicas práticas (Pro-tips), como melhores horários e sugestões de comida.
- O tom deve ser amigável e empolgante.
- Considere o 'ritmo' do viajante ao distribuir as atividades.
- Lembre o usuário sobre a necessidade de agendar restaurantes e o Genie+/Lightning Lanes com antecedência.
"""

    async def generate(self, itinerary_data: dict) -> str:
        """Recebe os dados e chama a API da OpenAI para gerar o roteiro."""
        system_prompt = self._get_generator_prompt(itinerary_data)
        
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

        print("INFO: Gerando o roteiro final com Chat Completions...")
        response = await self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            temperature=self.TEMPERATURE,
            max_tokens=self.MAX_TOKENS
        )

        final_itinerary = response.choices[0].message.content
        return final_itinerary or "Não foi possível gerar o roteiro neste momento."