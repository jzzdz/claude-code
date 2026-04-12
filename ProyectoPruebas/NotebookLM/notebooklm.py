"""
NotebookLM browser automation using Playwright.
Uses a persistent Chrome profile so Google login is saved between runs.

Selectors verified against NotebookLM UI as of March 2026.
"""

from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext

PROFILE_DIR = Path.home() / ".research-agent" / "browser-profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com"


async def _wait_for_login(page: Page) -> None:
    """Block until the user is logged in and NotebookLM home is visible."""
    from rich.console import Console
    console = Console()

    try:
        await page.wait_for_selector('[aria-label="Create new notebook"]', timeout=5000)
        return
    except Exception:
        pass

    console.print("\n[yellow]Inicia sesión en Google en la ventana del navegador.[/yellow]")
    console.print("[dim]Esperando autenticación (máx. 3 minutos)...[/dim]")
    await page.wait_for_selector('[aria-label="Create new notebook"]', timeout=180_000)
    console.print("[green]Sesión iniciada.[/green]")


async def _create_notebook(page: Page, title: str) -> None:
    """Click 'Create new notebook' and optionally rename it."""
    btn = page.locator('[aria-label="Create new notebook"]')
    await btn.wait_for(state="visible", timeout=15_000)
    await btn.click()

    # Wait until we're inside a notebook page
    await page.wait_for_url("**/notebook/**", timeout=20_000)

    if title:
        await _rename_notebook(page, title)


async def _rename_notebook(page: Page, title: str) -> None:
    """Rename the current notebook using the title input field."""
    try:
        title_field = page.locator('input.title-input').first
        await title_field.wait_for(state="visible", timeout=8_000)
        await title_field.triple_click()
        await title_field.fill(title)
        await title_field.press("Enter")
    except Exception:
        pass  # Cosmetic — continue even if rename fails


async def _add_sources(page: Page, urls: list[str]) -> int:
    """
    Add all YouTube/website URLs as sources in one dialog session.
    When a notebook is newly created, NotebookLM auto-opens the source dialog
    (URL contains ?addSource=true), so we skip clicking 'Add source'.
    Returns the number of URLs successfully submitted.
    """
    from rich.console import Console
    console = Console()

    try:
        # If the source dialog isn't already open, open it
        websites_btn = page.locator('button:has-text("Websites")').first
        try:
            await websites_btn.wait_for(state="visible", timeout=4_000)
        except Exception:
            # Dialog not open — click "Add sources" to open it
            add_btn = page.locator('[aria-label="Add source"]')
            await add_btn.wait_for(state="visible", timeout=15_000)
            await add_btn.click()
            await websites_btn.wait_for(state="visible", timeout=8_000)

        # Click "Websites"
        await websites_btn.click()

        # Paste all URLs (one per line) into the URL input
        url_input = page.locator('[aria-label="Enter URLs"]').first
        await url_input.wait_for(state="visible", timeout=8_000)
        await url_input.fill("\n".join(urls))

        # Click Insert
        insert_btn = page.locator('button:has-text("Insert")').first
        await insert_btn.wait_for(state="visible", timeout=8_000)
        await insert_btn.click()

        # Wait for dialog to close and sources to start processing
        await page.wait_for_timeout(3_000)
        return len(urls)

    except Exception as e:
        console.print(f"[red]Error agregando fuentes: {e}[/red]")
        return 0


async def upload_videos_to_notebooklm(
    video_urls: list[str],
    notebook_title: str = "Investigación",
) -> str:
    """
    Open NotebookLM, create a notebook, and add all video URLs as sources.
    Returns the URL of the created notebook.
    """
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # Remove stale lock file left by a previous crashed session
    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        lock_path = PROFILE_DIR / lock
        if lock_path.exists():
            lock_path.unlink()

    from rich.console import Console
    console = Console()

    async with async_playwright() as p:
        context: BrowserContext = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 900},
        )

        page = await context.new_page()
        await page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded")
        await _wait_for_login(page)

        console.print(f"[cyan]Creando notebook:[/cyan] {notebook_title}")
        await _create_notebook(page, notebook_title)

        notebook_url = page.url.split("?")[0]  # Strip ?addSource=true
        console.print(f"[green]Notebook creado:[/green] {notebook_url}\n")

        console.print(f"[cyan]Subiendo {len(video_urls)} videos como fuentes...[/cyan]")
        added = await _add_sources(page, video_urls)

        console.print(f"\n[bold green]{added} videos enviados a NotebookLM.[/bold green]")
        console.print("[yellow]NotebookLM procesará los videos en segundo plano.[/yellow]")
        console.print("[yellow]Cuando termine, usa 'Generate' para crear el audio overview o la guía de estudio.[/yellow]")

        await context.close()

    return notebook_url
