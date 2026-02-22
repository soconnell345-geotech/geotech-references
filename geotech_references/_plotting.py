"""Shared matplotlib helpers for reference figure plotting.

matplotlib is an optional dependency. Functions here are called only
from plot_* routines inside chapter modules.
"""


def get_pyplot():
    """Import and return matplotlib.pyplot, or raise ImportError."""
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for plotting. "
            "Install with: pip install matplotlib"
        )


def setup_engineering_plot(ax, title: str, xlabel: str, ylabel: str,
                           grid: bool = True) -> None:
    """Apply standard engineering plot formatting."""
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if grid:
        ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=9)
