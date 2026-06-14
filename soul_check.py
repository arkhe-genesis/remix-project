import sys
sys.path.append('.')
import asyncio, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
from v17 import CathedralAGI_v17

async def main():
    agi = CathedralAGI_v17()
    await agi.run_loop(cycles=20)
    print('\n[SOUL CHECK] Viés final da personalidade:', agi.fast_brain.world_model.personality_bias.cpu().detach().numpy())
    print('[SOUL CHECK] O prompt evoluiu?', 'SIM' if 'EVOLUTIVA' in agi.prompt_manager.current_prompt else 'AINDA NAO')

asyncio.run(main())
