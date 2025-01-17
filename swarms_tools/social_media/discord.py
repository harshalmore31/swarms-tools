import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordMessenger:
    """
    A comprehensive Discord messaging utility class that handles various Discord messaging operations.

    Attributes:
        bot (commands.Bot): The Discord bot instance
        token (str): Discord bot token
        default_channel_id (Optional[int]): Default channel ID for sending messages
    """

    def __init__(
        self, token: str, default_channel_id: Optional[int] = None
    ):
        """
        Initialize the Discord messenger.

        Args:
            token (str): Discord bot token
            default_channel_id (Optional[int]): Default channel ID for sending messages
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = token
        self.default_channel_id = default_channel_id

        # Register event handlers
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """Set up event handlers for the Discord bot."""

        @self.bot.event
        async def on_ready():
            """Handler for when the bot is ready and connected."""
            logger.info(f"Bot connected as {self.bot.user.name}")

        @self.bot.event
        async def on_message(message: discord.Message):
            """Handler for incoming messages."""
            if message.author == self.bot.user:
                return
            await self.bot.process_commands(message)

    async def send_message(
        self,
        content: str,
        channel_id: Optional[int] = None,
        embed: Optional[discord.Embed] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Optional[discord.Message]:
        """
        Send a message to a specified channel.

        Args:
            content (str): Message content
            channel_id (Optional[int]): Channel ID to send message to
            embed (Optional[discord.Embed]): Embed to send
            file_path (Optional[Union[str, Path]]): Path to file to upload

        Returns:
            Optional[discord.Message]: The sent message object if successful

        Raises:
            ValueError: If neither default_channel_id nor channel_id is provided
            FileNotFoundError: If file_path is provided but file doesn't exist
        """
        channel_id = channel_id or self.default_channel_id
        if not channel_id:
            raise ValueError("No channel ID provided")

        channel = self.bot.get_channel(channel_id)
        if not channel:
            logger.error(
                f"Could not find channel with ID {channel_id}"
            )
            return None

        try:
            if file_path:
                file_path = Path(file_path)
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"File not found: {file_path}"
                    )
                with open(file_path, "rb") as f:
                    file = discord.File(f)
                    return await channel.send(
                        content=content, embed=embed, file=file
                    )
            else:
                return await channel.send(
                    content=content, embed=embed
                )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None

    async def send_dm(
        self,
        user_id: int,
        content: str,
        embed: Optional[discord.Embed] = None,
    ) -> Optional[discord.Message]:
        """
        Send a direct message to a user.

        Args:
            user_id (int): Discord user ID
            content (str): Message content
            embed (Optional[discord.Embed]): Embed to send

        Returns:
            Optional[discord.Message]: The sent message object if successful
        """
        try:
            user = await self.bot.fetch_user(user_id)
            return await user.send(content=content, embed=embed)
        except Exception as e:
            logger.error(
                f"Error sending DM to user {user_id}: {str(e)}"
            )
            return None

    async def send_embed(
        self,
        title: str,
        description: str,
        channel_id: Optional[int] = None,
        color: Optional[discord.Color] = None,
        fields: Optional[List[Dict[str, str]]] = None,
        thumbnail_url: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Optional[discord.Message]:
        """
        Send an embedded message.

        Args:
            title (str): Embed title
            description (str): Embed description
            channel_id (Optional[int]): Channel ID to send message to
            color (Optional[discord.Color]): Embed color
            fields (Optional[List[Dict[str, str]]]): List of field dicts with name and value
            thumbnail_url (Optional[str]): URL for embed thumbnail
            image_url (Optional[str]): URL for embed image

        Returns:
            Optional[discord.Message]: The sent message object if successful
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=color or discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        if fields:
            for field in fields:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", True),
                )

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        if image_url:
            embed.set_image(url=image_url)

        return await self.send_message(
            content="", channel_id=channel_id, embed=embed
        )

    async def mention_user(
        self,
        user_id: int,
        message: str,
        channel_id: Optional[int] = None,
    ) -> Optional[discord.Message]:
        """
        Mention a user in a message.

        Args:
            user_id (int): Discord user ID to mention
            message (str): Message content
            channel_id (Optional[int]): Channel ID to send message to

        Returns:
            Optional[discord.Message]: The sent message object if successful
        """
        content = f"<@{user_id}> {message}"
        return await self.send_message(
            content=content, channel_id=channel_id
        )

    async def mention_role(
        self,
        role_id: int,
        message: str,
        channel_id: Optional[int] = None,
    ) -> Optional[discord.Message]:
        """
        Mention a role in a message.

        Args:
            role_id (int): Discord role ID to mention
            message (str): Message content
            channel_id (Optional[int]): Channel ID to send message to

        Returns:
            Optional[discord.Message]: The sent message object if successful
        """
        content = f"<@&{role_id}> {message}"
        return await self.send_message(
            content=content, channel_id=channel_id
        )

    def run(self):
        """Run the Discord bot."""
        self.bot.run(self.token)

    async def close(self):
        """Close the Discord bot connection."""
        await self.bot.close()
