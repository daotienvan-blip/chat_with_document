"""Điểm vào uvicorn: `uvicorn cwd_server.api.main:app`."""
from cwd_server.api.app import create_app
from cwd_server.container import build_container
from cwd_server.platform.config import get_settings
from cwd_server.platform.logging import setup_logging

setup_logging("api")
app = create_app(build_container(get_settings()))
