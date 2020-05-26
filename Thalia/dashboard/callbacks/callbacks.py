from .assets import register_assets_tab
from .summary import register_summary_tab
from .allocations import register_allocations_tab
from .dashboard import register_dashboard
from .overfitting import register_overfitting_tab


def register_callbacks(dashapp):
    """
    Collect all callbacks here

    Works as essentially react component routing.
    Whenever changes happen in an Input components chosen attribute
    function is called with Input and States as values and func
    returns values are sent to Output components
    """
    register_assets_tab(dashapp)
    register_summary_tab(dashapp)
    register_allocations_tab(dashapp)
    register_overfitting_tab(dashapp)
    register_dashboard(dashapp)
