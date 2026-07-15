from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminTextareaWidget

_SKIP_CLASSES = frozenset(
    {
        "bg-white",
        "text-font-default-light",
        "border-base-200",
        "dark:bg-base-900",
        "dark:border-base-700",
        "dark:text-font-default-dark",
    }
)
_FORCE_CLASSES = ("bg-base-900", "text-base-100", "border-base-700", "placeholder-base-400")


def cms_control_classes(base_classes: str) -> str:
    parts = [c for c in base_classes.split() if c not in _SKIP_CLASSES]
    parts.extend(_FORCE_CLASSES)
    return " ".join(dict.fromkeys(parts))


class CmsAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        base = UnfoldAdminTextInputWidget().attrs.get("class", "")
        super().__init__(attrs={"class": cms_control_classes(base), **(attrs or {})})


class CmsAdminTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None, rows=3):
        base = UnfoldAdminTextareaWidget().attrs.get("class", "")
        merged = {"class": cms_control_classes(base), "rows": rows, **(attrs or {})}
        super().__init__(attrs=merged)
