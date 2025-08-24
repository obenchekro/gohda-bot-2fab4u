import asyncio

class ClashService:
    async def clash_between_gohda_and_zaim(self, channel_id, gohda_id, zaim_id, logger):
        self.clash_active = True

        gohda_mention = f"<@{gohda_id}>"
        zaim_mention = f"<@{zaim_id}>"

        logger.info("🔥 Clash between Gohda and Zaim started.")
        gohda_turn = True

        try:
            while self.clash_active:
                if gohda_turn:
                    roast = await self.llm_client.generate_roast("gohda", zaim_mention, logger=logger)
                    if roast:
                        message = f"{zaim_mention} {roast}"
                        await self.send_message_in_chunks(channel_id, message, logger)
                else:
                    roast = await self.llm_client.generate_roast("zaim", gohda_mention, logger=logger)
                    if roast:
                        message = f"{gohda_mention} {roast}"
                        await self.send_message_in_chunks(channel_id, message, logger)

                gohda_turn = not gohda_turn
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Clash coroutine cancelled by unfart.")
        finally:
            await self.post_message(channel_id, "🛑 Gohda and Zaim stopped roasting. The arena is silent.", logger)
            logger.info("Clash ended.")
   
    async def trigger_clash(self, channel_id, gohda_id, zaim_id, logger):
        self.clash_active = True
        await self.post_message(channel_id, "⚔️ Fart detected. Gohda vs Zaim initiated!", logger)
        self.clash_task = asyncio.create_task(self.clash_between_gohda_and_zaim(channel_id, gohda_id, zaim_id, logger))

    async def stop_clash(self, channel_id, logger):
        self.clash_active = False
        if self.clash_task:
            self.clash_task.cancel()
            self.clash_task = None
        await self.post_message(channel_id, "💨 The fart has been unfarted. Peace restored.", logger)