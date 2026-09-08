from .javascript import JavaScriptAnalyzer
from .python import PythonAnalyzer
from .treesitter import TreeSitterJavaScriptAnalyzer, available as treesitter_available


def analyzers():
    items = [PythonAnalyzer()]
    if treesitter_available():
        items.append(TreeSitterJavaScriptAnalyzer())
    items.append(JavaScriptAnalyzer())
    return items

__all__ = ["analyzers", "PythonAnalyzer", "JavaScriptAnalyzer", "TreeSitterJavaScriptAnalyzer", "treesitter_available"]
