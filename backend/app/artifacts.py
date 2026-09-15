import re

import bleach
from bleach.css_sanitizer import CSSSanitizer


ALLOWED_TAGS = [
    "html",
    "head",
    "body",
    "meta",
    "title",
    "style",
    "header",
    "nav",
    "main",
    "section",
    "footer",
    "div",
    "span",
    "h1",
    "h2",
    "h3",
    "h4",
    "p",
    "a",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "button",
    "form",
    "input",
    "label",
    "article",
    "img",
]


ALLOWED_ATTRIBUTES = {
    "*": ["class", "id", "style"],
    "a": ["href", "target", "rel", "class", "id", "style"],
    "img": ["src", "alt", "class", "id", "style"],
    "input": [
        "type",
        "placeholder",
        "name",
        "value",
        "class",
        "id",
        "style",
    ],
    "form": ["action", "method", "class", "id", "style"],
    "meta": ["charset", "name", "content"],
}


ALLOWED_PROTOCOLS = [
    "http",
    "https",
    "mailto",
]


CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties={
        "color",
        "background",
        "background-color",
        "font-family",
        "font-size",
        "font-weight",
        "line-height",
        "text-align",
        "margin",
        "margin-top",
        "margin-right",
        "margin-bottom",
        "margin-left",
        "padding",
        "padding-top",
        "padding-right",
        "padding-bottom",
        "padding-left",
        "border",
        "border-radius",
        "display",
        "width",
        "height",
        "max-width",
        "min-height",
        "gap",
        "grid-template-columns",
        "box-shadow",
    }
)


def extract_html(text: str) -> str:
    if not text:
        return ""

    fenced = re.search(
        r"```(?:html|HTML)?\s*(.*?)```",
        text,
        flags=re.DOTALL,
    )

    if fenced:
        text = fenced.group(1).strip()

    doctype_match = re.search(
        r"<!DOCTYPE\s+html>",
        text,
        flags=re.IGNORECASE,
    )

    html_match = re.search(
        r"<html\b.*?</html>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if doctype_match and html_match:
        html = text[doctype_match.start():html_match.end()].strip()
    elif doctype_match:
        html = text[doctype_match.start():].strip()
    elif html_match:
        html = html_match.group(0).strip()
    else:
        html = text.strip()

    return html


def sanitize_html(text: str) -> str:
    html = extract_html(text)

    # Remove executable script blocks completely.
    html = re.sub(
        r"<script\b[^>]*>.*?</script\s*>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove other executable elements completely.
    html = re.sub(
        r"<iframe\b[^>]*>.*?</iframe\s*>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html = re.sub(
        r"<object\b[^>]*>.*?</object\s*>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html = re.sub(
        r"<embed\b[^>]*>",
        "",
        html,
        flags=re.IGNORECASE,
    )

    # Remove inline event handlers such as onclick/onerror.
    html = re.sub(
        r"\s+on[a-zA-Z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
        "",
        html,
        flags=re.IGNORECASE,
    )

    # Remove complete javascript/vbscript URL attributes.
    html = re.sub(
        r"\s+(href|src)\s*=\s*(['\"])\s*(?:javascript|vbscript)\s*:.*?\2",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove unquoted javascript/vbscript URL attributes.
    html = re.sub(
        r"\s+(href|src)\s*=\s*(?:javascript|vbscript)\s*:[^\s>]+",
        "",
        html,
        flags=re.IGNORECASE,
    )

    sanitized = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        css_sanitizer=CSS_SANITIZER,
        strip=True,
    )

    return sanitized