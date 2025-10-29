from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/template")
router = APIRouter(prefix="/client")


@router.get("/{page_name}", response_class=HTMLResponse)
async def serve_html_without_extension(request: Request, page_name: str):
    """
    Serves HTML files from the 'templates' directory without requiring the .html extension in the URL.
    """
    template_file = f"{page_name}.html"
    print(template_file)
    
    try:
        return templates.TemplateResponse(template_file, {"request": request})
    except Exception as e:
        # Handle cases where the file doesn't exist
        return HTMLResponse(content=f"<h1>Not Found</h1>", status_code=404)