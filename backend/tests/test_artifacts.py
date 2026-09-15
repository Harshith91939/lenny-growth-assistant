from app.artifacts import extract_html, sanitize_html


def test_extract_html_from_fenced_block():
    response = """
Here is your landing page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello</h1>
</body>
</html>
```
"""
    result = extract_html(response)

    assert result.startswith("<!DOCTYPE html>")
    assert "<h1>Hello</h1>" in result
    assert "Here is your landing page" not in result


def test_extract_html_without_code_fence():
    response = """
    <!DOCTYPE html>
    <html> <body> <h1>Hello</h1> </body> </html>
    """
    result = extract_html(response)

    assert "<html>" in result
    assert "<h1>Hello</h1>" in result


def test_sanitize_removes_script():
    html = """
    <!DOCTYPE html>
    <html> <body> <h1>Safe content</h1>
    <script>
        alert("XSS");
    </script>
    </body> </html>
    """
    result = sanitize_html(html)

    assert "<h1>Safe content</h1>" in result
    assert "<script" not in result
    assert "alert(" not in result


def test_sanitize_removes_event_handlers():
    html = """
    <html> <body>
    <img
        src="https://example.com/image.png"
        onerror="alert('XSS')"
        alt="test"
    >
    </body> </html>
    """
    result = sanitize_html(html)

    assert "onerror" not in result
    assert "alert(" not in result


def test_sanitize_removes_javascript_urls():
    html = """
    <html> <body>
    <a href="javascript:alert('XSS')">
        Click me
    </a>
    </body> </html>
    """
    result = sanitize_html(html)

    assert "javascript:" not in result.lower()
    assert "alert(" not in result


def test_safe_html_is_preserved():
    html = """
    <!DOCTYPE html>
    <html> <head>
    <style>
        body {
            font-family: Arial;
        }
    </style>
    </head> <body>
    <section class="hero">
        <h1>Product-Market Fit Playbook</h1>
        <p>
            Build products people want.
        </p>
        <a href="https://example.com">
            Learn more
        </a>
    </section>
    </body> </html>
    """
    result = sanitize_html(html)

    assert "Product-Market Fit Playbook" in result
    assert "Build products people want." in result
    assert "https://example.com" in result
    assert "<style>" in result