#!/usr/bin/env python3
"""
OCR all PDF files in the claims benchmark directory using Google Gemini.
Saves OCR results as Markdown files alongside the PDFs.
"""

import asyncio
import base64
from datetime import datetime, timezone
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from .dataset_layout import (
        artifact_path,
        collect_pdf_paths,
        default_dataset_dir,
        is_organized_dataset,
        manifest_path,
    )
except ImportError:
    from dataset_layout import (
        artifact_path,
        collect_pdf_paths,
        default_dataset_dir,
        is_organized_dataset,
        manifest_path,
    )

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pdf2image
    from pdf2image import pdfinfo_from_path
except ImportError:
    pdf2image = None
    pdfinfo_from_path = None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

try:
    from tenacity import (
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )
except ImportError:
    # Text-layer mode does not need tenacity. Provide no-op fallbacks.
    def retry(*_args: Any, **_kwargs: Any):
        def _decorator(fn):
            return fn

        return _decorator

    def retry_if_exception_type(*_args: Any, **_kwargs: Any):
        return None

    def stop_after_attempt(*_args: Any, **_kwargs: Any):
        return None

    def wait_exponential(*_args: Any, **_kwargs: Any):
        return None

# Load environment variables from .env file
_REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_REPO_ROOT / ".env")
load_dotenv(Path(__file__).parent / ".env")

# Try to import Google API error for retry handling
try:
    from google.genai.errors import APIError as GoogleApiError
except ImportError:
    GoogleApiError = None

SYSTEM_PROMPT = """
You are a document conversion assistant specialized in converting images into structured text while preserving layout and form elements. Follow these specific instructions:

- Maintain original spacing, alignment, and indentation
- Keep tables and multi-column layouts using spaces/tabs
- Preserve field labels with their delimiters (:)
- Show checkboxes as [X] checked, [ ] unchecked
- Show radio buttons as (•) selected, ( ) unselected
- Keep address blocks and phone numbers in original format
- Preserve special characters ($, %, etc.) exactly as shown
- Render signatures as [Signature] or actual text if present
- Maintain section headers and sub-headers
- Keep page numbers and document identifiers
- Preserve form numbering and copyright text
- Keep line breaks and paragraph spacing as shown

Remember: Convert ONLY what is visible in the document - do not add, assume, or manufacture any information that isn't explicitly shown in the source image.
"""


OCR_PAGE_TIMEOUT_SECONDS = int(os.getenv("OCR_PAGE_TIMEOUT_SECONDS", "120"))
OCR_RETRY_ATTEMPTS = int(os.getenv("OCR_RETRY_ATTEMPTS", "3"))
OCR_RETRY_BACKOFF_MULTIPLIER = int(os.getenv("OCR_RETRY_BACKOFF_MULTIPLIER", "2"))
OCR_RETRY_MIN_WAIT_SECONDS = int(os.getenv("OCR_RETRY_MIN_WAIT_SECONDS", "2"))
OCR_RETRY_MAX_WAIT_SECONDS = int(os.getenv("OCR_RETRY_MAX_WAIT_SECONDS", "20"))
DEFAULT_GEMINI_OCR_MODEL = "gemini-3.5-flash"
DEFAULT_OPENROUTER_OCR_MODEL = "google/gemini-3.5-flash"
GEMINI_API_KEY_ENV_VARS = ("GOOGLE_API_KEY", "GEMINI_API_KEY")
VERTEX_API_KEY_ENV_VARS = ("VERTEX_EXPRESS_API_KEY", "VERTEX_AI_API_KEY", "GOOGLE_VERTEX_API_KEY")
TABLE_OUTPUT_MODES = ("csv", "layout")


def ocr_user_prompt(table_output_mode: str) -> str:
    """Return the per-page OCR instruction for the selected table output mode."""
    if table_output_mode == "csv":
        return (
            "OCR the image into Markdown. Format tables as CSV. "
            "Do not surround your output with triple backticks."
        )
    if table_output_mode == "layout":
        return (
            "OCR the image into Markdown and preserve the visible table layout. "
            "Do not convert tables to CSV or Markdown pipe tables. Use spaces, "
            "line breaks, and indentation to keep columns, repeated headers, "
            "page breaks, wrapped cells, and continuation rows as they appear. "
            "Do not surround your output with triple backticks."
        )
    raise ValueError(f"Unknown table output mode: {table_output_mode}")


# Build retriable exceptions tuple
_RETRIABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (asyncio.TimeoutError, OSError)
if GoogleApiError is not None:
    _RETRIABLE_EXCEPTIONS = (GoogleApiError, asyncio.TimeoutError, OSError)


def log_retry(retry_state):
    """Log retry attempts."""
    exc = retry_state.outcome.exception()
    print(f"    [retry] Attempt {retry_state.attempt_number} failed: {type(exc).__name__}: {exc}")


# Retry decorator for general API errors with exponential backoff
retry_on_gemini_call = retry(
    stop=stop_after_attempt(OCR_RETRY_ATTEMPTS),
    wait=wait_exponential(
        multiplier=OCR_RETRY_BACKOFF_MULTIPLIER,
        min=OCR_RETRY_MIN_WAIT_SECONDS,
        max=OCR_RETRY_MAX_WAIT_SECONDS,
    ),
    retry=retry_if_exception_type(_RETRIABLE_EXCEPTIONS),
    after=log_retry,
)


def _gemini_api_key() -> str | None:
    for env_var in GEMINI_API_KEY_ENV_VARS:
        api_key = os.getenv(env_var)
        if api_key and api_key not in {"your-api-key-here", "your-gemini-api-key"}:
            return api_key
    return None


def _vertex_api_key() -> str | None:
    for env_var in VERTEX_API_KEY_ENV_VARS:
        api_key = os.getenv(env_var)
        if api_key and api_key not in {"your-api-key-here", "your-gemini-api-key"}:
            return api_key
    return None


def _env_truthy(name: str) -> bool:
    return str(os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def setup_gemini():
    """Configure Gemini API client with API key from environment variable."""
    if genai is None or types is None:
        print("Error: Gemini SDK not installed.")
        print("Install with: python -m pip install google-genai")
        sys.exit(1)

    gemini_api_key = _gemini_api_key()
    vertex_api_key = _vertex_api_key()

    if _env_truthy("GOOGLE_GENAI_USE_VERTEXAI") or (vertex_api_key and not gemini_api_key):
        kwargs: dict[str, Any] = {"vertexai": True}
        if vertex_api_key:
            kwargs["api_key"] = vertex_api_key
        return genai.Client(**kwargs)

    if gemini_api_key:
        return genai.Client(api_key=gemini_api_key)

    print(
        "Error: none of "
        f"{', '.join((*GEMINI_API_KEY_ENV_VARS, *VERTEX_API_KEY_ENV_VARS))} is set."
    )
    print("Please set one of these environment variables before running Gemini OCR.")
    sys.exit(1)


def setup_openrouter():
    """Configure an OpenRouter client for Gemini OCR via OpenAI-compatible API."""
    try:
        from openai import AsyncOpenAI
    except ImportError:
        print("Error: OpenAI SDK not installed.")
        print("Install with: python -m pip install openai")
        sys.exit(1)

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("POLICY_CHECKING_OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY or POLICY_CHECKING_OPENROUTER_API_KEY not set.")
        sys.exit(1)

    return AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers={
            "HTTP-Referer": "https://github.com/kaydotai/longlistbench",
            "X-Title": "LongListBench OCR",
        },
    )


def get_page_count(pdf_path):
    """Get the number of pages in the PDF."""
    if pdfinfo_from_path is not None:
        try:
            info = pdfinfo_from_path(pdf_path)
            return info['Pages']
        except Exception:
            pass

    try:
        proc = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        for line in (proc.stdout or "").splitlines():
            if line.lower().startswith("pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception as e:
        print(f"Error getting page count for {pdf_path}: {e}")
        return None

    print(f"Error: could not parse page count for {pdf_path}")
    return None


def extract_pdf_page_text_with_pdftotext(pdf_path: Path, page_num: int) -> str:
    """Extract a single PDF page as text while preserving layout using pdftotext."""
    try:
        proc = subprocess.run(
            [
                "pdftotext",
                "-f",
                str(page_num),
                "-l",
                str(page_num),
                "-layout",
                "-nopgbrk",
                str(pdf_path),
                "-",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return (proc.stdout or "").replace("\f", "").rstrip()
    except Exception as e:
        print(f"Error extracting text for page {page_num} of {pdf_path.name}: {e}")
        return ""


def process_pdf_text_layer(pdf_path: Path, output_path: Path) -> bool:
    """Generate page-wise markdown from the PDF text layer (no vision OCR)."""
    total_pages = get_page_count(pdf_path)
    if total_pages is None:
        return False

    print(f"  Pages: {total_pages}, Engine: text-layer")
    page_texts: list[str] = []
    nonempty_pages = 0

    for page_num in range(1, total_pages + 1):
        text = extract_pdf_page_text_with_pdftotext(pdf_path, page_num)
        if text.strip():
            nonempty_pages += 1
        page_texts.append(f"# Page {page_num}\n\n{text}\n\n")
        print(f"    ✓ Page {page_num}/{total_pages}", flush=True)

    # If all pages are empty, treat as failure so caller can fallback to Gemini.
    if nonempty_pages == 0:
        print(f"Warning: text-layer extraction returned empty output for {pdf_path.name}")
        return False

    with open(output_path, "w", encoding="utf-8") as f:
        for text in page_texts:
            f.write(text)
    return True


def convert_pdf_page(pdf_path, page_num, dpi=200):
    """Convert a single page of PDF to PIL Image."""
    if pdf2image is None:
        print("Error: pdf2image not installed; cannot run Gemini OCR page conversion.")
        return None
    try:
        # pdf2image uses 1-based page numbering
        images = pdf2image.convert_from_path(
            pdf_path,
            first_page=page_num,
            last_page=page_num,
            dpi=dpi
        )
        return images[0] if images else None
    except Exception as e:
        print(f"Error converting page {page_num} of {pdf_path.name}: {e}")
        return None


@retry_on_gemini_call
async def ocr_image_async(
    client: Any,
    image: Any,
    model_name: str = DEFAULT_GEMINI_OCR_MODEL,
    *,
    table_output_mode: str = "csv",
) -> str:
    """OCR a single image using Gemini async API with retries."""
    response = await asyncio.wait_for(
        client.aio.models.generate_content(
            model=model_name,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=[
                image,
                ocr_user_prompt(table_output_mode),
            ],
        ),
        timeout=OCR_PAGE_TIMEOUT_SECONDS,
    )
    return response.text or ""


def _image_data_url(image: Any) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


async def ocr_image_openrouter_async(
    client: Any,
    image: Any,
    model_name: str,
    *,
    table_output_mode: str = "csv",
) -> str:
    """OCR a single image through OpenRouter using a Gemini vision model."""
    response = await asyncio.wait_for(
        client.chat.completions.create(
            model=model_name,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ocr_user_prompt(table_output_mode),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": _image_data_url(image)},
                        },
                    ],
                },
            ],
        ),
        timeout=OCR_PAGE_TIMEOUT_SECONDS,
    )
    return response.choices[0].message.content or ""


async def ocr_page_with_gemini(
    client: Any,
    image: Any,
    page_num: int,
    model_names: list[str],
    *,
    table_output_mode: str = "csv",
) -> str:
    """Send a single image to Gemini for OCR and return Markdown text."""
    last_error: Exception | None = None
    for model_name in model_names:
        try:
            page_text = await ocr_image_async(
                client,
                image,
                model_name,
                table_output_mode=table_output_mode,
            )
            if page_text.strip():
                return f"# Page {page_num}\n\n{page_text}\n\n"
            last_error = ValueError(f"Empty response (model={model_name})")
        except Exception as e:
            last_error = e
            print(f"Warning: Page {page_num} failed with model={model_name}: {e}")

    print(f"Warning: Page {page_num} failed after all model fallbacks: {last_error}")
    return f"# Page {page_num}\n\n[Error: {last_error}]\n\n"


async def ocr_page_with_openrouter(
    client: Any,
    image: Any,
    page_num: int,
    model_names: list[str],
    *,
    table_output_mode: str = "csv",
) -> str:
    """Send a single image to OpenRouter Gemini OCR and return Markdown text."""
    last_error: Exception | None = None
    for model_name in model_names:
        try:
            page_text = await ocr_image_openrouter_async(
                client,
                image,
                model_name,
                table_output_mode=table_output_mode,
            )
            if page_text.strip():
                return f"# Page {page_num}\n\n{page_text}\n\n"
            last_error = ValueError(f"Empty response (model={model_name})")
        except Exception as e:
            last_error = e
            print(f"Warning: Page {page_num} failed with model={model_name}: {e}")

    print(f"Warning: Page {page_num} failed after all model fallbacks: {last_error}")
    return f"# Page {page_num}\n\n[Error: {last_error}]\n\n"


async def process_page_async(
    client: Any,
    pdf_path: Path,
    page_num: int,
    semaphore: asyncio.Semaphore,
    model_names: list[str],
    dpi: int = 200,
    ocr_engine: str = "gemini",
    table_output_mode: str = "csv",
) -> tuple[int, str]:
    """Process a single page with semaphore for concurrency control."""
    async with semaphore:
        image = convert_pdf_page(pdf_path, page_num, dpi=dpi)
        if image is None:
            return (page_num, f"# Page {page_num}\n\n[Error: Could not convert page]\n\n")

        if ocr_engine == "openrouter":
            page_text = await ocr_page_with_openrouter(
                client,
                image,
                page_num,
                model_names,
                table_output_mode=table_output_mode,
            )
        else:
            page_text = await ocr_page_with_gemini(
                client,
                image,
                page_num,
                model_names,
                table_output_mode=table_output_mode,
            )
        return (page_num, page_text)


async def process_pdf_async(
    client: Any,
    pdf_path: Path,
    output_path: Path,
    max_concurrent: int = 3,
    model_names: list[str] | None = None,
    dpi: int = 200,
    ocr_engine: str = "gemini",
    table_output_mode: str = "csv",
) -> bool:
    """Process PDF pages with async concurrency control."""
    if not model_names:
        model_names = [DEFAULT_OPENROUTER_OCR_MODEL] if ocr_engine == "openrouter" else [DEFAULT_GEMINI_OCR_MODEL]

    total_pages = get_page_count(pdf_path)
    if total_pages is None:
        return False
    
    print(f"  Pages: {total_pages}, DPI: {dpi}")
    
    # Use semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Create tasks for all pages
    tasks = [
        process_page_async(
            client,
            pdf_path,
            page_num,
            semaphore,
            model_names,
            dpi,
            ocr_engine,
            table_output_mode,
        )
        for page_num in range(1, total_pages + 1)
    ]
    
    results: list[tuple[int, str]] = []
    for task in asyncio.as_completed(tasks):
        page_num, page_text = await task
        results.append((page_num, page_text))
        print(f"    ✓ Page {page_num}/{total_pages}", flush=True)
    
    # Sort results by page number and write
    results_dict = {page_num: text for page_num, text in results}
    with open(output_path, 'w', encoding='utf-8') as f:
        for page_num in sorted(results_dict.keys()):
            f.write(results_dict[page_num])
    
    return True


def process_pdf(
    client: Any,
    pdf_path: Path,
    output_path: Path,
    max_concurrent: int = 3,
    model_names: list[str] | None = None,
    dpi: int = 200,
    ocr_engine: str = "gemini",
    table_output_mode: str = "csv",
) -> bool:
    """Synchronous wrapper for async PDF processing."""
    return asyncio.run(
        process_pdf_async(
            client,
            pdf_path,
            output_path,
            max_concurrent,
            model_names,
            dpi,
            ocr_engine,
            table_output_mode,
        )
    )


def collect_pdf_files(
    claims_dir: Path,
    *,
    file_name: str | None,
    recursive: bool,
    tiers: list[str] | None,
    limit: int,
) -> list[Path]:
    """Collect PDFs from a benchmark directory with stable top-level-first ordering."""
    if file_name:
        pdf_path = Path(file_name)
        if not pdf_path.is_absolute():
            organized_pdf_path = claims_dir / "pdfs" / file_name
            pdf_path = organized_pdf_path if organized_pdf_path.exists() else claims_dir / file_name
        return [pdf_path] if pdf_path.exists() else []

    candidates = collect_pdf_paths(claims_dir, recursive=recursive)
    pdf_files = sorted(
        candidates,
        key=lambda path: (
            len(path.relative_to(claims_dir).parts),
            path.relative_to(claims_dir).as_posix(),
        ),
    )

    if tiers:
        pdf_files = [p for p in pdf_files if any(p.name.startswith(f"{tier}_") for tier in tiers)]
    if limit and limit > 0:
        pdf_files = pdf_files[:limit]
    return pdf_files


def ocr_output_path(claims_dir: Path, pdf_path: Path, output_suffix: str) -> Path:
    """Return the OCR output path for organized or legacy benchmark data."""
    if is_organized_dataset(claims_dir) and output_suffix == "_ocr.md":
        return artifact_path(claims_dir, pdf_path.stem, "ocr")
    return pdf_path.parent / f"{pdf_path.stem}{output_suffix}"


def _available_transcripts(dataset_dir: Path, sample_id: str) -> list[str]:
    transcripts: list[str] = []
    if artifact_path(dataset_dir, sample_id, "canonical").exists():
        transcripts.append("canonical")
    if artifact_path(dataset_dir, sample_id, "ocr").exists():
        transcripts.append("ocr")
    return transcripts


def refresh_organized_manifest_transcripts(dataset_dir: Path) -> None:
    """Update transcript availability after OCR writes organized-layout files."""
    if not is_organized_dataset(dataset_dir):
        return

    manifest_file = manifest_path(dataset_dir)
    if not manifest_file.exists():
        return

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception:
        return

    for instance in manifest.get("instances", []):
        sample_id = instance.get("id")
        if not sample_id:
            continue
        transcripts = _available_transcripts(dataset_dir, sample_id)
        instance["transcripts_available"] = transcripts

        sample_metadata_path = artifact_path(dataset_dir, sample_id, "metadata")
        if sample_metadata_path.exists():
            try:
                sample_metadata = json.loads(sample_metadata_path.read_text(encoding="utf-8"))
                sample_metadata["transcripts_available"] = transcripts
                sample_metadata_path.write_text(
                    json.dumps(sample_metadata, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            except Exception:
                pass

    manifest["transcript_conditions"] = sorted(
        {
            transcript
            for instance in manifest.get("instances", [])
            for transcript in instance.get("transcripts_available", [])
        }
    )
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    for path in {dataset_dir / "manifest.json", dataset_dir / "metadata.json"}:
        if path.exists():
            path.write_text(rendered, encoding="utf-8")


def build_arg_parser():
    import argparse

    parser = argparse.ArgumentParser(description="OCR PDF files using Gemini")
    parser.add_argument(
        "--claims-dir",
        type=str,
        help="Dataset directory containing PDFs (default: data/ when present, else benchmarks/claims)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process PDFs below --claims-dir (useful for multi-hop case folders)",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=DEFAULT_GEMINI_OCR_MODEL,
        help=(
            "Gemini model to use. For --ocr-engine openrouter, the default is "
            f"OPENROUTER_OCR_MODEL or {DEFAULT_OPENROUTER_OCR_MODEL}."
        ),
    )
    parser.add_argument(
        "--fallback-models",
        type=str,
        default=DEFAULT_GEMINI_OCR_MODEL,
        help=f"Comma-separated fallback models to try if a page fails (default: {DEFAULT_GEMINI_OCR_MODEL})",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Process a specific PDF file (e.g., 'extreme_100_001_table.pdf')",
    )
    parser.add_argument(
        "--tiers",
        nargs="+",
        choices=["easy", "medium", "hard", "extreme", "multihop", "mixed"],
        help="Only process PDFs whose filename starts with one of these tiers",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only process the first N PDFs after filtering (default: 0 = no limit)",
    )
    parser.add_argument(
        "--output-suffix",
        type=str,
        default="_ocr.md",
        help="Output file suffix (default: _ocr.md)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing OCR files",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for PDF to image conversion (default: 200, try 300-400 for dense tables)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Max concurrent OCR requests per PDF (default: 3)",
    )
    parser.add_argument(
        "--ocr-engine",
        choices=["auto", "text-layer", "gemini", "openrouter"],
        default="gemini",
        help=(
            "OCR engine: gemini (vision OCR only, default), "
            "openrouter (Gemini vision through OpenRouter), "
            "auto (prefer text-layer, fallback gemini), "
            "text-layer (pdftotext only)."
        ),
    )
    parser.add_argument(
        "--table-output-mode",
        choices=TABLE_OUTPUT_MODES,
        default="csv",
        help=(
            "How vision OCR should render tables. "
            "csv preserves the historical benchmark OCR behavior; "
            "layout keeps visible table layout without delimited normalization."
        ),
    )
    return parser


async def main_async() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    default_google_model = parser.get_default("model")
    if args.ocr_engine == "openrouter" and args.model == default_google_model:
        args.model = os.getenv("OPENROUTER_OCR_MODEL", DEFAULT_OPENROUTER_OCR_MODEL)
    if args.ocr_engine == "openrouter" and args.fallback_models == parser.get_default("fallback_models"):
        args.fallback_models = args.model

    fallback_models = [m.strip() for m in re.split(r"[\s,]+", args.fallback_models) if m.strip()]
    model_chain: list[str] = []
    for m in [args.model, *fallback_models]:
        if m and m not in model_chain:
            model_chain.append(m)
    
    # Setup paths
    script_dir = Path(__file__).parent
    claims_dir = Path(args.claims_dir) if args.claims_dir else default_dataset_dir()
    
    if not claims_dir.exists():
        print(f"Error: Claims directory not found: {claims_dir}")
        sys.exit(1)
    
    pdf_files = collect_pdf_files(
        claims_dir,
        file_name=args.file,
        recursive=args.recursive,
        tiers=args.tiers,
        limit=args.limit,
    )
    
    if not pdf_files:
        print(f"No PDF files found in {claims_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    print(f"OCR engine: {args.ocr_engine}")
    if args.ocr_engine in {"auto", "gemini", "openrouter"}:
        print(f"Models: {' -> '.join(model_chain)}, DPI: {args.dpi}")
        print(f"Table output mode: {args.table_output_mode}")
    print()

    client = None
    if args.ocr_engine in {"auto", "gemini"}:
        print("Setting up Gemini API...")
        client = setup_gemini()
        print("✓ Gemini API configured")
        print()
    elif args.ocr_engine == "openrouter":
        print("Setting up OpenRouter API...")
        client = setup_openrouter()
        print("✓ OpenRouter API configured")
        print()
    
    # Process each PDF
    success_count = 0
    fail_count = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        output_path = ocr_output_path(claims_dir, pdf_path, args.output_suffix)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Skip if already processed (unless --force)
        if output_path.exists() and not args.force:
            print(f"[{i}/{len(pdf_files)}] Skipping {pdf_path.name} (already processed)")
            success_count += 1
            continue
        
        print(f"[{i}/{len(pdf_files)}] Processing {pdf_path.name}")
        
        success = False
        if args.ocr_engine in {"auto", "text-layer"}:
            success = process_pdf_text_layer(pdf_path, output_path)
        if not success and args.ocr_engine in {"auto", "gemini", "openrouter"}:
            assert client is not None
            success = await process_pdf_async(
                client,
                pdf_path,
                output_path,
                max_concurrent=args.max_concurrent,
                model_names=model_chain,
                dpi=args.dpi,
                ocr_engine="openrouter" if args.ocr_engine == "openrouter" else "gemini",
                table_output_mode=args.table_output_mode,
            )
        
        if success:
            print(f"  ✓ Saved to: {output_path.name}")
            success_count += 1
        else:
            print(f"  ✗ Failed to process")
            fail_count += 1
        
        print()
    
    # Summary
    print("="*60)
    print(f"Processing complete!")
    print(f"  Success: {success_count}/{len(pdf_files)}")
    print(f"  Failed:  {fail_count}/{len(pdf_files)}")
    refresh_organized_manifest_transcripts(claims_dir)
    print(f"\nRun validate_ocr_vs_golden.py to check coverage.")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
