from openai import AsyncOpenAI
from dotenv import load_dotenv
import logging
import asyncio
import os
import json
import backoff
import openai
from pathlib import Path

class GPT:
    def __init__(self, log_level: int = logging.INFO, model: str = "gpt-5-mini", temperature: float = 0.1):
        self.logger = logging.getLogger("GPT")
        self.logger.setLevel(log_level)
        if not self.logger.hasHandlers():
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        project_root = Path(__file__).resolve().parents[1]
        load_dotenv(dotenv_path=project_root / ".env")
        openai_api_key = os.getenv("OPENAI_API_KEY_OAI")
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model
        self.temperature = temperature
        self.semaphore = asyncio.Semaphore(10)
        self.logger.info("GPT initialized")

    async def analyze(self, input_df: pl.DataFrame) -> pl.DataFrame:
        async def process_single_group(group_key, group_df) -> dict:
            try:
                # Extract the grouping columns
                host_name, group_leader_pid = group_key
                
                user_context = f"""<user>
    <name>{group_df["user.name"].unique()[0]}</name>
    <department>{group_df["user.department"].unique()[0]}</department>
    <title>{group_df["user.title"].unique()[0]}</title>
    <city>{group_df["user.geo.city_name"].unique()[0]}</city>
    <state>{group_df["user.geo.region_name"].unique()[0]}</state>
</user>
                """
                
                host_context = f"""<host>
    <macos_version>{group_df["host.os.family"][0]}</macos_version>
    <name>{host_name}</name>
</host>
                """
        
                collected_data = group_df.sort("@timestamp").select(
                    "@timestamp", "process.pid", "process.parent.pid", "process.parent.name", "process.command_line", "process.working_directory"
                ).to_pandas().to_markdown()
        
                system_message = system_prompt + user_context + host_context
                user_message = f"""
Beginning of commands for analysis:
Processes: {collected_data}
"""
                analysis =  await self.make_completion(system_message, user_message)
                result = {
                    "host.name": host_name,
                    "process.group_leader.pid": group_leader_pid, 
                    "analysis": analysis
                }
                return result
            except Exception as e:
                self.logger.error(f"Error processing group {group_key}: {e}")
                return {
                    "host.name": host_name,
                    "process.group_leader.pid": group_leader_pid,
                    "error": str(e),
                }
        grouped = input_df.group_by(["host.name", "process.group_leader.pid"])
        tasks = [
            process_single_group(group_key, group_df)
            for group_key, group_df in grouped
        ]

        results = await asyncio.gather(*tasks)
        return pl.DataFrame(results)

    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_time=60, max_tries=6)
    async def make_completion(self, system_message: str, user_message: str) -> str:
        async with self.semaphore:
            completion = await self.client.responses.create(
                model = self.model,
                instructions = system_message,
                temperature = self.temperature, 
                input = [
                    {"role": "user", "content": user_message}
                ]
            )
            return completion.output_text

    async def print_messages(self, system_message, user_message):
        pass
