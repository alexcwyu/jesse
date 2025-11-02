from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix='/lsp-config', tags=['LSP Configuration'])

@router.get("")
def get_lsp_config()->JSONResponse:
    from jesse.services.env import ENV_VALUES
    
    return JSONResponse(
        {'ws_port': ENV_VALUES['LSP_PORT'] if 'LSP_PORT' in ENV_VALUES else 9011,
         'ws_path':'/lsp'}, status_code=200)