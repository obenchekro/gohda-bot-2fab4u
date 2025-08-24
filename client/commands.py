from discord import app_commands, Interaction
from environments import GUILD_ID

import discord

class Commands:
    def __init__(self, client, logger, gohda_id, zaim_id, ):
        self.client = client
        self.logger = logger
        self.tree = client.tree
        self.gohda_id = gohda_id
        self.zaim_id = zaim_id

    async def setup(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)
        self.tree.copy_global_to(guild=guild)
        self.tree.clear_commands(guild=guild)

        commands = [
            self.help,
            self.gif,
            self.fart,
            self.unfart,
            self.news,
            self.vg,
            self.vnts,
            self.csgo,
        ]

        for command in commands:
            self.tree.add_command(command, guild=guild)

        await self.tree.sync(guild=guild)


    @app_commands.command(name="help", description="Displays the bot's command manual")
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(
            "**📘 Bot Command Manual**\n"
            "🗣️ `@bot [text]` → Shitpost reply\n"
            "🖼️ `/gif` → Sends a meme gif (VG/VN-related)\n"
            "⚔️ `/fart` → Starts the Gohda vs Zaim roast battle\n"
            "💨 `/unfart` → Stops the roast battle\n"
            "🎯 `/help` → Displays this help menu\n"
            "📈 `/news` → Sends financial/crypto/ETF news\n"
            "🎮 `/vg` → Sends the latest /vg/ announcements\n"
            "📰 `/vnts` → Sends visual novel translation updates\n"
            "🔫 `/csgo` → Sends the latest CS:GO trade trends",
            ephemeral=True
        )

    @app_commands.command(name="gif", description="Sends a meme gif")
    async def gif(self, interaction: Interaction):
        await self.client.send_gif(interaction.channel.id, self.logger)

    @app_commands.command(name="fart", description="Starts the Gohda vs Zaim roast battle")
    async def fart(self, interaction: Interaction):
        await interaction.response.send_message("⚔️ Fart detected. Gohda vs Zaim initiated!")

    @app_commands.command(name="unfart", description="Stops the Gohda vs Zaim roast battle")
    async def unfart(self, interaction: Interaction):
        await self.client.stop_clash(interaction.channel.id, self.logger)

    @app_commands.command(name="news", description="Fetches crypto/ETF/stock news")
    async def news(self, interaction: Interaction):
        await self.client.dispatch_news_financial_markets(interaction.user.id, interaction.channel.id, self.logger)

    @app_commands.command(name="vg", description="Fetches /vg/ announcements")
    async def vg(self, interaction: Interaction):
        await self.client.dispatch_new_vg_annoucements(interaction.channel.id, self.logger)

    @app_commands.command(name="vnts", description="Fetches visual novel translation updates")
    async def vnts(self, interaction: Interaction):
        await self.client.dispatch_vn_tl_updates_daily(interaction.channel.id, self.logger)

    @app_commands.command(name="csgo", description="Fetches CS:GO trade and skin news")
    async def csgo(self, interaction: Interaction):
        await self.client.dispatch_news_csgo_trades_skins(interaction.user.id, interaction.channel.id, self.logger)
