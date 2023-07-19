from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    BOT_TOKEN: str
    BOT_NICKNAME: str
    GH_ACCOUNT_TOKEN: str
    GH_ORGANIZATION_NICKNAME: str

    # This id's used for automatically add issue to scrum board
    # and set default column such a backlog
    # If you want to use scrum bard just set GH_SCRUM_STATE to True
    # and pass project id, field if, and default field state id
    GH_SCRUM_STATE: bool = False
    GH_SCRUM_ID: str = 'PVT_kwDOBaPiZM4AFiz-'
    GH_SCRUM_FIELD_ID: str = 'PVTSSF_lADOBaPiZM4AFiz-zgDMeOc'
    GH_SCRUM_FIELD_DEFAULT_STATE: str = '4a4a1bb5'

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")
